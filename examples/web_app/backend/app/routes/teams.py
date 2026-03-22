from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models import Team, Agent

router = APIRouter(prefix="/teams", tags=["teams"])


class TeamCreate(BaseModel):
    name: str
    agent_ids: List[int]


@router.get("")
async def list_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).order_by(Team.created_at.desc()))
    teams = result.scalars().all()
    out = []
    for t in teams:
        # resolve agent names
        agent_result = await db.execute(
            select(Agent).where(Agent.id.in_(t.agent_ids or []))
        )
        agents = agent_result.scalars().all()
        out.append(
            {
                "id": t.id,
                "name": t.name,
                "agents": [
                    {"id": a.id, "name": a.name, "avatar_emoji": a.avatar_emoji}
                    for a in agents
                ],
            }
        )
    return out


@router.post("")
async def create_team(
    body: TeamCreate, db: AsyncSession = Depends(get_db)
):
    if not body.agent_ids or len(body.agent_ids) > 5:
        raise HTTPException(
            status_code=400, detail="A team needs 1‑5 agents"
        )
    # verify agents exist
    result = await db.execute(select(Agent).where(Agent.id.in_(body.agent_ids)))
    found = result.scalars().all()
    if len(found) != len(body.agent_ids):
        raise HTTPException(status_code=404, detail="One or more agents not found")

    team = Team(user_id=1, name=body.name, agent_ids=body.agent_ids)
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return {"id": team.id, "name": team.name, "agent_ids": team.agent_ids}


@router.delete("/{team_id}")
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await db.delete(team)
    await db.commit()
    return {"ok": True}
