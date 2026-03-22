"""
Game simulation service — powered by Google Gemini.

Each possession the LLM receives the full game state + all player profiles
and generates a structured JSON play event. This replaces the old template
/ random number approach entirely.
"""

import json
import os
import time
import redis as sync_redis

from google import genai
from google.genai import types

from app.config import REDIS_URL, UPLOAD_DIR, GEMINI_API_KEY

# ── Redis client ──────────────────────────────────────────────────────────────
_redis = sync_redis.from_url(REDIS_URL)

# ── Gemini client ─────────────────────────────────────────────────────────────
_genai_client = genai.Client(api_key=GEMINI_API_KEY)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_agent_profile(agent: dict) -> str:
    """Read memory.md + skills.md from the agent's stored directory."""
    path = agent.get("profile_storage_path", "")
    parts = [f"## 球員：{agent['name']}\n"]

    for fname, label in [("memory.md", "記憶 / 背景"), ("skills.md", "技能 / 能力")]:
        full_path = os.path.join(path, fname)
        if os.path.exists(full_path):
            with open(full_path, "r", errors="replace") as f:
                content = f.read().strip()
            parts.append(f"### {label}\n{content}\n")
        else:
            parts.append(f"### {label}\n（無檔案）\n")

    stats = (
        f"投籃={agent.get('shooting', 75)} 防守={agent.get('defense', 70)} "
        f"傳球={agent.get('passing', 70)} 速度={agent.get('speed', 70)} "
        f"體力={agent.get('stamina', 70)}"
    )
    parts.append(f"### 數值屬性\n{stats}\n")
    return "\n".join(parts)


def _build_system_prompt(home_agents: list[dict], away_agents: list[dict]) -> str:
    home_profiles = "\n\n".join(_load_agent_profile(a) for a in home_agents)
    away_profiles = "\n\n".join(_load_agent_profile(a) for a in away_agents)

    home_names = ", ".join(a["name"] for a in home_agents)
    away_names = ", ".join(a["name"] for a in away_agents)

    return f"""你是一個超級擬真的籃球比賽模擬器，負責模擬一場充滿個性的AI球員比賽。

## 主隊球員（Home）：{home_names}
{home_profiles}

## 客隊球員（Away）：{away_names}
{away_profiles}

## 規則
- 每次收到指令時，你必須模擬一個回合（possession）。
- **你的輸出必須是一個合法的 JSON，不帶任何 Markdown 格式，直接輸出 JSON。**
- JSON 格式如下：
{{
  "text": "一段生動的比賽描述，必須根據球員性格和技能自然呈現，100字以內",
  "pts": 0
}}
- "pts" 是本回合得分（0、2 或 3 分）。
- 請務必讓球員性格、記憶和技能真實影響每個回合的結果和描述。
- 輪流讓主隊和客隊進攻；你在每次 prompt 中都會被指定攻守方，請遵守。
- 可以有失誤（turnover）、封堵（block）、籃板（rebound）等各種結果，pts=0。
- 用繁體中文描述比賽。"""


def _parse_llm_response(text: str) -> dict:
    """Extract the JSON object from the LLM response, handling markdown fences."""
    # Strip ```json ... ``` if present
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text.strip())


# ── Main simulation ───────────────────────────────────────────────────────────

def simulate_match(
    match_id: int,
    home_agents: list[dict],
    away_agents: list[dict],
    quarters: int = 4,
    quarter_possessions: int = 12,
):
    """Run a full LLM-simulated game and publish events to Redis Pub/Sub."""
    channel = f"match:{match_id}:events"
    home_score = 0
    away_score = 0

    home_names = [a["name"] for a in home_agents] or ["主隊球員"]
    away_names = [a["name"] for a in away_agents] or ["客隊球員"]

    # ── Build system prompt from agent profiles ────────────────────────────
    system_prompt = _build_system_prompt(home_agents, away_agents)

    # ── Start a multi-turn chat session so the LLM has game history ────────
    chat = _genai_client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.85,
            max_output_tokens=256,
        ),
    )

    # ── Kick-off event ─────────────────────────────────────────────────────
    _publish(channel, {
        "type": "system",
        "quarter": 0,
        "text": f"🏀 比賽即將開始！{' vs '.join(home_names[:1] + away_names[:1])} — 讓我們看看 AI 球員如何應戰！",
        "home_score": 0,
        "away_score": 0,
    })
    time.sleep(1)

    for q in range(1, quarters + 1):
        _publish(channel, {
            "type": "system",
            "quarter": q,
            "text": f"─── 第 {q} 節 ───",
            "home_score": home_score,
            "away_score": away_score,
        })
        time.sleep(0.4)

        for pos in range(quarter_possessions):
            is_home = pos % 2 == 0
            offense_team = "主隊（Home）" if is_home else "客隊（Away）"
            defense_team = "客隊（Away）" if is_home else "主隊（Home）"

            prompt = (
                f"第 {q} 節，第 {pos + 1} 次進攻。"
                f"現在 {offense_team} 持球進攻，{defense_team} 防守。"
                f"當前比分：主隊 {home_score} — 客隊 {away_score}。"
                "請模擬這個回合，輸出合法 JSON。"
            )

            try:
                response = chat.send_message(prompt)
                event_data = _parse_llm_response(response.text)
                text = event_data.get("text", "比賽繼續...")
                pts = int(event_data.get("pts", 0))
            except Exception as e:
                # Fallback if LLM fails or JSON is malformed
                text = f"{'主隊' if is_home else '客隊'} 進行進攻..."
                pts = 0

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
            time.sleep(1.2)  # LLM calls take a moment; pace the stream

    # ── Final buzzer ───────────────────────────────────────────────────────
    winner = "主隊" if home_score > away_score else ("客隊" if away_score > home_score else "平局")
    _publish(channel, {
        "type": "final",
        "quarter": quarters,
        "text": f"🏁 終場哨響！最終比分：主隊 {home_score} — 客隊 {away_score}。{'勝利者：' + winner if winner != '平局' else '精彩平局！'}",
        "home_score": home_score,
        "away_score": away_score,
    })
    return home_score, away_score


def _publish(channel: str, data: dict):
    _redis.publish(channel, json.dumps(data, ensure_ascii=False))
