from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
import os, hashlib, random

from app.database import get_db
from app.models import Agent
from app.config import UPLOAD_DIR

router = APIRouter(prefix="/agents", tags=["agents"])

EMOJIS = ["🏀", "⛹️", "🔥", "💪", "🎯", "🦾", "👾", "🤖", "🧬", "⚡"]

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _generate_stats(content: bytes) -> dict:
    """Derive deterministic-ish stats from file content so the same files
    always produce the same agent — gives the user a sense of causality."""
    h = int(hashlib.sha256(content).hexdigest(), 16)
    base = 60
    return {
        "shooting": base + (h % 35),
        "defense": base + ((h >> 8) % 35),
        "passing": base + ((h >> 16) % 35),
        "speed": base + ((h >> 24) % 35),
        "stamina": base + ((h >> 32) % 35),
    }


@router.get("")
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).order_by(Agent.created_at.desc()))
    agents = result.scalars().all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "avatar_emoji": a.avatar_emoji,
            "shooting": a.shooting,
            "defense": a.defense,
            "passing": a.passing,
            "speed": a.speed,
            "stamina": a.stamina,
        }
        for a in agents
    ]


@router.post("")
async def create_agent(
    name: str = Form(...),
    user_id: int = Form(1),
    memory_file: UploadFile = File(...),
    skills_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    agent_dir = os.path.join(UPLOAD_DIR, str(uuid4()))
    os.makedirs(agent_dir, exist_ok=True)

    mem_bytes = await memory_file.read()
    ski_bytes = await skills_file.read()

    with open(os.path.join(agent_dir, "memory.md"), "wb") as f:
        f.write(mem_bytes)
    with open(os.path.join(agent_dir, "skills.md"), "wb") as f:
        f.write(ski_bytes)

    stats = _generate_stats(mem_bytes + ski_bytes)

    agent = Agent(
        user_id=user_id,
        name=name,
        avatar_emoji=random.choice(EMOJIS),
        profile_storage_path=agent_dir,
        **stats,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return {
        "id": agent.id,
        "name": agent.name,
        "avatar_emoji": agent.avatar_emoji,
        **stats,
    }


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.delete(agent)
    await db.commit()
    return {"ok": True}
