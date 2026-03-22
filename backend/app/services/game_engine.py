"""
Game simulation service — powered by Google Gemini 2.5 Flash.

Uses stateless generate_content per possession. Robustly extracts JSON
from any response format (plain, fenced, with preamble text).
"""

import json
import os
import random
import re
import time
import redis as sync_redis

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from app.config import REDIS_URL, GEMINI_API_KEY

# ── Redis client ──────────────────────────────────────────────────────────────
_redis = sync_redis.from_url(REDIS_URL)

# ── Gemini client ─────────────────────────────────────────────────────────────
_genai_client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"

# ── Profile loader ────────────────────────────────────────────────────────────

def _load_agent_profile(agent: dict) -> str:
    """Return a compact one-liner agent summary for the system prompt."""
    path = agent.get("profile_storage_path", "")
    name = agent["name"]

    mem, ski = "", ""
    for fname, var in (("memory.md", "mem"), ("skills.md", "ski")):
        full_path = os.path.join(path, fname) if path else ""
        if full_path and os.path.exists(full_path):
            with open(full_path, "r", errors="replace") as f:
                content = f.read().strip()[:250]  # cap to save tokens
            if var == "mem":
                mem = content
            else:
                ski = content

    stats = (
        f"投={agent.get('shooting', 75):.0f} "
        f"守={agent.get('defense', 70):.0f} "
        f"傳={agent.get('passing', 70):.0f} "
        f"速={agent.get('speed', 70):.0f} "
        f"耐={agent.get('stamina', 70):.0f}"
    )
    profile_parts = [f"【{name}】{stats}"]
    if mem:
        profile_parts.append(f"背景：{mem}")
    if ski:
        profile_parts.append(f"技能：{ski}")
    return " | ".join(profile_parts)


def _build_system_prompt(home_agents: list[dict], away_agents: list[dict]) -> str:
    home_lines = "\n".join(_load_agent_profile(a) for a in home_agents)
    away_lines = "\n".join(_load_agent_profile(a) for a in away_agents)
    home_names = "\u3001".join(a["name"] for a in home_agents)
    away_names = "\u3001".join(a["name"] for a in away_agents)
    home_count = len(home_agents)
    away_count = len(away_agents)

    # Build roster-aware constraint
    roster_rules = []
    if home_count == 1:
        roster_rules.append(
            f"\u4e3b\u968a\u53ea\u6709 1 \u4eba\uff08{home_names}\uff09\uff0c\u7d55\u5c0d\u4e0d\u80fd\u63cf\u8ff0\u50b3\u7403\u7d66\u968a\u53cb\u6216\u5c0b\u627e\u968a\u53cb\u7a7a\u6a94\u7684\u5834\u666f\u3002"
        )
    if away_count == 1:
        roster_rules.append(
            f"\u5ba2\u968a\u53ea\u6709 1 \u4eba\uff08{away_names}\uff09\uff0c\u7d55\u5c0d\u4e0d\u80fd\u63cf\u8ff0\u50b3\u7403\u7d66\u968a\u53cb\u6216\u5c0b\u627e\u968a\u53cb\u7a7a\u6a94\u7684\u5834\u666f\u3002"
        )
    roster_constraint = "\n".join(roster_rules)

    return f"""\u4f60\u662f\u7c43\u7403\u6bd4\u8cfd\u6a21\u64ec\u5668\u3002\u6839\u64da\u7403\u54e1\u500b\u6027\u548c\u6280\u80fd\u6a21\u64ec\u6bcf\u500b\u9032\u653b\u56de\u5408\u3002

\u4e3b\u968a\uff08{home_names}\uff0c\u5171 {home_count} \u4eba\uff09:
{home_lines}

\u5ba2\u968a\uff08{away_names}\uff0c\u5171 {away_count} \u4eba\uff09:
{away_lines}

\u53ea\u56de\u50b3 JSON\uff0c\u683c\u5f0f\uff1a{{"text":"\u7e41\u9ad4\u4e2d\u6587\u63cf\u8ff020\u5b57\u5167","pts":2}}
pts \u53ea\u80fd\u662f 0/2/3\uff1b\u5931\u8aa4/\u88ab\u5c01/\u672a\u9032=0\u3002\u8b93\u7403\u54e1\u6027\u683c\u548c\u6280\u80fd\u771f\u5be6\u5f71\u97ff\u7d50\u679c\u3002\u4e0d\u8981\u4efb\u4f55\u8aaa\u660e\u6587\u5b57\u3002
{roster_constraint}"""


def _extract_json(raw: str) -> dict:
    """
    Extract the first JSON object from an arbitrary string.
    Handles: plain JSON, markdown fences, preamble text.
    """
    if not raw:
        raise ValueError("Empty response")

    # Strategy 1: Try direct parse
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from ```json ... ``` fences
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))

    # Strategy 3: Find first {...} object in the response
    brace = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
    if brace:
        return json.loads(brace.group(0))

    raise ValueError(f"No JSON found in: {raw[:200]!r}")


def _call_llm(system_prompt: str, user_prompt: str, retries: int = 4) -> dict:
    """Call Gemini with retry on 429 rate-limit errors."""
    last_exc = None
    for attempt in range(retries):
        try:
            response = _genai_client.models.generate_content(
                model=MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.9,
                    max_output_tokens=200,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            data = _extract_json(response.text)
            pts = int(data.get("pts", 0))
            if pts not in (0, 2, 3):
                pts = 0
            text = str(data.get("text", "")).strip()
            return {"text": text, "pts": pts}

        except ClientError as e:
            last_exc = e
            if e.status_code == 429 and attempt < retries - 1:
                wait = 65 * (attempt + 1)
                print(f"[game_engine] 429 rate-limit — waiting {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
            else:
                raise

        except (ValueError, json.JSONDecodeError) as e:
            last_exc = e
            print(f"[game_engine] JSON parse error attempt {attempt}: {e!r}")
            if attempt < retries - 1:
                time.sleep(2)

    raise RuntimeError(f"LLM call failed after {retries} attempts: {last_exc}")


# ── Main simulation ───────────────────────────────────────────────────────────

def simulate_match(
    match_id: int,
    home_agents: list[dict],
    away_agents: list[dict],
    quarters: int = 4,
    quarter_possessions: int = 12,
):
    channel = f"match:{match_id}:events"
    home_score = 0
    away_score = 0

    home_names = [a["name"] for a in home_agents] or ["主隊"]
    away_names = [a["name"] for a in away_agents] or ["客隊"]

    system_prompt = _build_system_prompt(home_agents, away_agents)

    _publish(channel, {
        "type": "system", "quarter": 0,
        "text": f"🏀 比賽開始！{home_names[0]} vs {away_names[0]}",
        "home_score": 0, "away_score": 0,
    })
    time.sleep(0.5)

    for q in range(1, quarters + 1):
        _publish(channel, {
            "type": "system", "quarter": q,
            "text": f"─── 第 {q} 節 ───",
            "home_score": home_score, "away_score": away_score,
        })
        time.sleep(0.3)

        for pos in range(quarter_possessions):
            is_home = pos % 2 == 0
            offense = "主隊" if is_home else "客隊"
            defense = "客隊" if is_home else "主隊"
            off_agents = home_agents if is_home else away_agents
            def_agents = away_agents if is_home else home_agents
            off_players = "、".join(a["name"] for a in off_agents)
            def_players = "、".join(a["name"] for a in def_agents)
            off_count = len(off_agents)

            # Randomly assign ball-handler + primary defender for this possession
            # This breaks LLM name-bias (e.g. always writing Jordan as the scorer)
            ball_handler = random.choice(off_agents)["name"]
            primary_defender = random.choice(def_agents)["name"]

            # Tell the LLM exactly how many teammates the ball-handler has
            if off_count == 1:
                teammate_hint = f"註意：進攻方只有 {off_players} 一人，絕對不可描述傳球給隊友。"
            else:
                teammate_hint = f"進攻方共 {off_count} 人在場。"

            user_prompt = (
                f"第{q}節 第{pos+1}回合。"
                f"{offense}持球（{off_players}\uff09，{defense}防守（{def_players}）。"
                f"比分：主隊{home_score}-客隊{away_score}。"
                f"{teammate_hint}"
                f"本回合主要持球者是「{ball_handler}」，主要防守者是「{primary_defender}」。"
                f"請以{ball_handler}為主角描述這個進攻回合。只回傳JSON。"
            )

            pts = 0
            text = ""
            try:
                result = _call_llm(system_prompt, user_prompt)
                text = result["text"]
                pts = result["pts"]
            except Exception as exc:
                text = f"{offense} 繼續進攻..."
                pts = 0
                print(f"[game_engine] Unrecoverable error q={q} pos={pos}: {exc}")

            if is_home:
                home_score += pts
            else:
                away_score += pts

            _publish(channel, {
                "type": "play", "quarter": q,
                "text": text or f"{offense} 進行進攻...",
                "home_score": home_score, "away_score": away_score,
            })
            # 3.5s delay per call → ~17 calls/min, safely under 20 rpm free tier
            time.sleep(3.5)

    # Final
    if home_score > away_score:
        result_txt = "主隊勝利 🏆"
    elif away_score > home_score:
        result_txt = "客隊勝利 🏆"
    else:
        result_txt = "雙方平局！"

    _publish(channel, {
        "type": "final", "quarter": quarters,
        "text": f"🏁 終場！主隊 {home_score} — 客隊 {away_score}。{result_txt}",
        "home_score": home_score, "away_score": away_score,
    })
    return home_score, away_score


def _publish(channel: str, data: dict):
    _redis.publish(channel, json.dumps(data, ensure_ascii=False))
