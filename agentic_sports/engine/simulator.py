import random
import time
from typing import List, Callable, Dict, Any, Optional

from agentic_sports.agent.profile import Agent
from agentic_sports.engine.llm import LLMClient

class Simulator:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", 
                 on_event: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.llm = LLMClient(api_key=api_key, model=model)
        self.on_event = on_event

    def _build_system_prompt(self, home_agents: List[Agent], away_agents: List[Agent]) -> str:
        home_lines = "\n".join(a.to_prompt_string() for a in home_agents)
        away_lines = "\n".join(a.to_prompt_string() for a in away_agents)
        home_names = "、".join(a.name for a in home_agents)
        away_names = "、".join(a.name for a in away_agents)
        home_count = len(home_agents)
        away_count = len(away_agents)

        roster_rules = []
        if home_count == 1:
            roster_rules.append(
                f"主隊只有 1 人（{home_names}），絕對不能描述傳球給隊友或尋找隊友空檔的場景。"
            )
        if away_count == 1:
            roster_rules.append(
                f"客隊只有 1 人（{away_names}），絕對不能描述傳球給隊友或尋找隊友空檔的場景。"
            )
        roster_constraint = "\n".join(roster_rules)

        return f"""你是籃球比賽模擬器。根據球員個性和技能模擬每個進攻回合。

主隊（{home_names}，共 {home_count} 人）:
{home_lines}

客隊（{away_names}，共 {away_count} 人）:
{away_lines}

只回傳 JSON，格式：{{"text":"繁體中文描述20字內","pts":2}}
pts 只能是 0/2/3；失誤/被封/未進=0。讓球員性格和技能真實影響結果。不要任何說明文字。
{roster_constraint}"""

    def _publish(self, event_data: dict):
        if self.on_event:
            self.on_event(event_data)

    def run_match(self, home_team: List[Agent], away_team: List[Agent], 
                 quarters: int = 4, quarter_possessions: int = 12, 
                 delay_between_plays: float = 3.5):
        
        home_score = 0
        away_score = 0

        home_names_list = [a.name for a in home_team] or ["主隊"]
        away_names_list = [a.name for a in away_team] or ["客隊"]

        system_prompt = self._build_system_prompt(home_team, away_team)

        self._publish({
            "type": "system", "quarter": 0,
            "text": f"🏀 比賽開始！{home_names_list[0]} vs {away_names_list[0]}",
            "home_score": 0, "away_score": 0,
        })
        time.sleep(0.5)

        for q in range(1, quarters + 1):
            self._publish({
                "type": "system", "quarter": q,
                "text": f"─── 第 {q} 節 ───",
                "home_score": home_score, "away_score": away_score,
            })
            time.sleep(0.3)

            for pos in range(quarter_possessions):
                is_home = pos % 2 == 0
                offense = "主隊" if is_home else "客隊"
                defense = "客隊" if is_home else "主隊"
                off_agents = home_team if is_home else away_team
                def_agents = away_team if is_home else home_team
                
                off_players = "、".join(a.name for a in off_agents)
                def_players = "、".join(a.name for a in def_agents)
                off_count = len(off_agents)

                ball_handler = random.choice(off_agents).name
                primary_defender = random.choice(def_agents).name

                if off_count == 1:
                    teammate_hint = f"注意：進攻方只有 {off_players} 一人，絕對不可描述傳球給隊友。"
                else:
                    teammate_hint = f"進攻方共 {off_count} 人在場。"

                user_prompt = (
                    f"第{q}節 第{pos+1}回合。"
                    f"{offense}持球（{off_players}），{defense}防守（{def_players}）。"
                    f"比分：主隊{home_score}-客隊{away_score}。"
                    f"{teammate_hint}"
                    f"本回合主要持球者是「{ball_handler}」，主要防守者是「{primary_defender}」。"
                    f"請以{ball_handler}為主角描述這個進攻回合。只回傳JSON。"
                )

                try:
                    result = self.llm.call(system_prompt, user_prompt)
                    text = result["text"]
                    pts = result["pts"]
                except Exception as exc:
                    text = f"{offense} 繼續進攻..."
                    pts = 0
                    print(f"[Simulator] Unrecoverable error q={q} pos={pos}: {exc}")

                if is_home:
                    home_score += pts
                else:
                    away_score += pts

                self._publish({
                    "type": "play", "quarter": q,
                    "text": text or f"{offense} 進行進攻...",
                    "home_score": home_score, "away_score": away_score,
                })
                
                if delay_between_plays > 0:
                    time.sleep(delay_between_plays)

        if home_score > away_score:
            result_txt = "主隊勝利 🏆"
        elif away_score > home_score:
            result_txt = "客隊勝利 🏆"
        else:
            result_txt = "雙方平局！"

        self._publish({
            "type": "final", "quarter": quarters,
            "text": f"🏁 終場！主隊 {home_score} — 客隊 {away_score}。{result_txt}",
            "home_score": home_score, "away_score": away_score,
        })
        
        return home_score, away_score
