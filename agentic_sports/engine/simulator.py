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
        home_names = " and ".join(a.name for a in home_agents)
        away_names = " and ".join(a.name for a in away_agents)
        home_count = len(home_agents)
        away_count = len(away_agents)

        roster_rules = []
        if home_count == 1:
            roster_rules.append(
                f"Home team has only 1 player ({home_names}), absolutely NO describing passing to teammates."
            )
        if away_count == 1:
            roster_rules.append(
                f"Away team has only 1 player ({away_names}), absolutely NO describing passing to teammates."
            )
        roster_constraint = "\n".join(roster_rules)

        return f"""You are a basketball game simulator. Simulate each offensive possession based on player personality and skills.

Home Team ({home_names}, {home_count} total):
{home_lines}

Away Team ({away_names}, {away_count} total):
{away_lines}

Return JSON only, format: {{"text":"English description within 20 words","pts":2}}
pts must be 0/2/3; turnover/blocked/missed=0. Let player personality and skills truly affect the result. No explanation text.
{roster_constraint}"""

    def _publish(self, event_data: dict):
        if self.on_event:
            self.on_event(event_data)

    def run_match(self, home_team: List[Agent], away_team: List[Agent], 
                 quarters: int = 4, quarter_possessions: int = 12, 
                 delay_between_plays: float = 3.5):
        
        home_score = 0
        away_score = 0

        home_names_list = [a.name for a in home_team] or ["Home Team"]
        away_names_list = [a.name for a in away_team] or ["Away Team"]

        system_prompt = self._build_system_prompt(home_team, away_team)

        self._publish({
            "type": "system", "quarter": 0,
            "text": f"🏀 Game Start! {home_names_list[0]} vs {away_names_list[0]}",
            "home_score": 0, "away_score": 0,
        })
        time.sleep(0.5)

        for q in range(1, quarters + 1):
            self._publish({
                "type": "system", "quarter": q,
                "text": f"─── Quarter {q} ───",
                "home_score": home_score, "away_score": away_score,
            })
            time.sleep(0.3)

            for pos in range(quarter_possessions):
                is_home = pos % 2 == 0
                offense = "Home" if is_home else "Away"
                defense = "Away" if is_home else "Home"
                off_agents = home_team if is_home else away_team
                def_agents = away_team if is_home else home_team
                
                off_players = " and ".join(a.name for a in off_agents)
                def_players = " and ".join(a.name for a in def_agents)
                off_count = len(off_agents)

                ball_handler = random.choice(off_agents).name
                primary_defender = random.choice(def_agents).name

                if off_count == 1:
                    teammate_hint = f"Note: The offensive side has only {off_players} alone, absolutely NO describing passing to teammates."
                else:
                    teammate_hint = f"Offensive side has {off_count} players on court."

                user_prompt = (
                    f"Quarter {q}, Possession {pos+1}."
                    f"{offense} Possession ({off_players}), {defense} Defense ({def_players})."
                    f"Score: Home {home_score} - Away {away_score}."
                    f"{teammate_hint}"
                    f"The primary ball handler is '{ball_handler}', and the primary defender is '{primary_defender}'."
                    f"Please describe this offensive possession with {ball_handler} as the protagonist. Return JSON only."
                )

                try:
                    result = self.llm.call(system_prompt, user_prompt)
                    text = result["text"]
                    pts = result["pts"]
                except Exception as exc:
                    text = f"{offense} continues the attack..."
                    pts = 0
                    print(f"[Simulator] Unrecoverable error q={q} pos={pos}: {exc}")

                if is_home:
                    home_score += pts
                else:
                    away_score += pts

                self._publish({
                    "type": "play", "quarter": q,
                    "text": text or f"{offense} is attacking...",
                    "home_score": home_score, "away_score": away_score,
                })
                
                if delay_between_plays > 0:
                    time.sleep(delay_between_plays)

        if home_score > away_score:
            result_txt = "Home Team Wins 🏆"
        elif away_score > home_score:
            result_txt = "Away Team Wins 🏆"
        else:
            result_txt = "It's a Draw!"

        self._publish({
            "type": "final", "quarter": quarters,
            "text": f"🏁 Final! Home {home_score} — Away {away_score}. {result_txt}",
            "home_score": home_score, "away_score": away_score,
        })
        
        return home_score, away_score
