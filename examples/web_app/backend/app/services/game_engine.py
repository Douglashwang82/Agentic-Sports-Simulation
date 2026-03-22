"""
Game simulation service facade — uses the agentic_sports library.
"""

import json
import redis as sync_redis

from agentic_sports import Simulator, Agent
from app.config import REDIS_URL, GEMINI_API_KEY

_redis = sync_redis.from_url(REDIS_URL)

def simulate_match(
    match_id: int,
    home_agents: list[dict],
    away_agents: list[dict],
    quarters: int = 4,
    quarter_possessions: int = 12,
):
    channel = f"match:{match_id}:events"

    # Callback to send redis events
    def on_event(data: dict):
        _redis.publish(channel, json.dumps(data, ensure_ascii=False))

    # Convert DB dicts to Library Agents
    home_team = []
    for a in home_agents:
        agent = Agent.from_markdown(
            profile_dir=a.get("profile_storage_path", ""),
            name=a["name"],
            stats=a
        )
        home_team.append(agent)

    away_team = []
    for a in away_agents:
        agent = Agent.from_markdown(
            profile_dir=a.get("profile_storage_path", ""),
            name=a["name"],
            stats=a
        )
        away_team.append(agent)

    sim = Simulator(api_key=GEMINI_API_KEY, on_event=on_event)
    return sim.run_match(home_team, away_team, quarters, quarter_possessions)
