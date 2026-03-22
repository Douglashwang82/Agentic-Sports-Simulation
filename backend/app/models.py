from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agents = relationship("Agent", back_populates="owner")
    teams = relationship("Team", back_populates="owner")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    avatar_emoji = Column(String(10), default="🏀")
    profile_storage_path = Column(String(500))
    # Base stats generated on upload (0‑100 scale)
    shooting = Column(Float, default=75.0)
    defense = Column(Float, default=75.0)
    passing = Column(Float, default=75.0)
    speed = Column(Float, default=75.0)
    stamina = Column(Float, default=75.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="agents")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    agent_ids = Column(JSON, default=list)  # list of up to 5 agent ids
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="teams")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending | live | finished
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    winner_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    replay_path = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
