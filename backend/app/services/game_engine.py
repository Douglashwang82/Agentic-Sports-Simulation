"""
Game simulation service.

Uses a simple deterministic engine that produces play‑by‑play events.
Each "possession" is one call; in the future this will call an LLM.
"""

import random, json, time
import redis as sync_redis
from app.config import REDIS_URL

_redis = sync_redis.from_url(REDIS_URL)

PLAY_TEMPLATES = [
    "{player} drives to the basket and scores a layup!",
    "{player} pulls up from mid-range... swish!",
    "{player} crosses over, spins, and finishes with a reverse layup!",
    "{player} catches and shoots from downtown... it's good! Three pointer!",
    "{player} posts up, turns, and hits a fadeaway jumper!",
    "{player} runs the fast break and slams it home with authority!",
    "{player} finds the open lane and floats one in!",
    "{player} with a step-back three... nothing but net!",
    "Turnover! {defender} steals the ball!",
    "{player} drives but gets blocked by {defender}!",
    "{player} takes the shot... it rims out. Rebound by {defender}.",
    "{player} pulls up but misses. Tough shot.",
]

THREE_PLAYS = {3, 7}  # indices that are 3-pointers
MISS_PLAYS = {8, 9, 10, 11}  # indices that are misses / turnovers


def simulate_match(
    match_id: int,
    home_agents: list[dict],
    away_agents: list[dict],
    quarters: int = 4,
    quarter_possessions: int = 12,
):
    """Run a full simulated game and publish events to Redis Pub/Sub."""
    channel = f"match:{match_id}:events"
    home_score = 0
    away_score = 0

    home_names = [a["name"] for a in home_agents] or ["Home-1"]
    away_names = [a["name"] for a in away_agents] or ["Away-1"]

    # Publish game start
    _publish(channel, {
        "type": "system",
        "quarter": 0,
        "text": "🏀 The game is about to begin!",
        "home_score": 0,
        "away_score": 0,
    })
    time.sleep(1)

    for q in range(1, quarters + 1):
        _publish(channel, {
            "type": "system",
            "quarter": q,
            "text": f"--- Quarter {q} ---",
            "home_score": home_score,
            "away_score": away_score,
        })
        time.sleep(0.5)

        for pos in range(quarter_possessions):
            is_home = pos % 2 == 0
            offense = home_names if is_home else away_names
            defense = away_names if is_home else home_names

            idx = random.randint(0, len(PLAY_TEMPLATES) - 1)
            template = PLAY_TEMPLATES[idx]
            text = template.format(
                player=random.choice(offense),
                defender=random.choice(defense),
            )

            if idx not in MISS_PLAYS:
                pts = 3 if idx in THREE_PLAYS else 2
                if is_home:
                    home_score += pts
                else:
                    away_score += pts

            _publish(channel, {
                "type": "play",
                "quarter": q,
                "text": text,
                "home_score": home_score,
                "away_score": away_score,
            })
            time.sleep(0.6)  # pacing for smooth frontend

    # Final whistle
    _publish(channel, {
        "type": "final",
        "quarter": quarters,
        "text": "🏁 That's the final buzzer! Game over!",
        "home_score": home_score,
        "away_score": away_score,
    })
    return home_score, away_score


def _publish(channel: str, data: dict):
    _redis.publish(channel, json.dumps(data))
