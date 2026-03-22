from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import asyncio
import redis.asyncio as aioredis

from app.database import get_db
from app.models import Match, Team, Agent
from app.config import REDIS_URL
from app.services.game_engine import simulate_match

router = APIRouter(prefix="/matches", tags=["matches"])


class ChallengeRequest(BaseModel):
    home_team_id: int
    away_team_id: int


@router.get("")
async def list_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).order_by(Match.created_at.desc()).limit(20))
    matches = result.scalars().all()
    return [
        {
            "id": m.id,
            "home_team_id": m.home_team_id,
            "away_team_id": m.away_team_id,
            "status": m.status,
            "home_score": m.home_score,
            "away_score": m.away_score,
        }
        for m in matches
    ]


@router.post("")
async def create_match(body: ChallengeRequest, db: AsyncSession = Depends(get_db)):
    # Verify both teams exist
    for tid in (body.home_team_id, body.away_team_id):
        res = await db.execute(select(Team).where(Team.id == tid))
        if not res.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"Team {tid} not found")

    match = Match(
        home_team_id=body.home_team_id,
        away_team_id=body.away_team_id,
        status="pending",
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return {"id": match.id, "status": match.status}


@router.post("/{match_id}/start")
async def start_match(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status != "pending":
        raise HTTPException(status_code=400, detail="Match is not pending")

    # Gather agents for both teams
    home_team = (await db.execute(select(Team).where(Team.id == match.home_team_id))).scalar_one()
    away_team = (await db.execute(select(Team).where(Team.id == match.away_team_id))).scalar_one()

    async def _get_agents(agent_ids):
        if not agent_ids:
            return []
        res = await db.execute(select(Agent).where(Agent.id.in_(agent_ids)))
        return [{"id": a.id, "name": a.name} for a in res.scalars().all()]

    home_agents = await _get_agents(home_team.agent_ids)
    away_agents = await _get_agents(away_team.agent_ids)

    match.status = "live"
    await db.commit()

    # Run the simulation in a background thread (it's CPU/IO‑bound + sleep)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        None,
        _run_and_finalize,
        match.id,
        home_agents,
        away_agents,
    )

    return {"id": match.id, "status": "live"}


def _run_and_finalize(match_id, home_agents, away_agents):
    """Runs in a thread – simulates and then updates DB synchronously."""
    from sqlalchemy import create_engine, update
    from sqlalchemy.orm import Session as SyncSession
    from app.config import DATABASE_URL

    home_score, away_score = simulate_match(match_id, home_agents, away_agents)

    sync_url = DATABASE_URL.replace("+asyncpg", "")
    sync_engine = create_engine(sync_url)
    with SyncSession(sync_engine) as session:
        session.execute(
            update(Match)
            .where(Match.id == match_id)
            .values(
                status="finished",
                home_score=home_score,
                away_score=away_score,
                winner_team_id=None,  # TODO: resolve
            )
        )
        session.commit()
    sync_engine.dispose()


@router.websocket("/{match_id}/stream")
async def stream_match(websocket: WebSocket, match_id: int):
    await websocket.accept()
    conn = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = conn.pubsub()
    await pubsub.subscribe(f"match:{match_id}:events")

    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await websocket.send_text(msg["data"])
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        await pubsub.unsubscribe(f"match:{match_id}:events")
        await conn.aclose()
