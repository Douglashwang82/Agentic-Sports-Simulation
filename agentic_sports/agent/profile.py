import os

class Agent:
    def __init__(self, name: str, shooting: float = 75, defense: float = 75, passing: float = 75, speed: float = 75, stamina: float = 75, memory: str = "", skills: str = ""):
        self.name = name
        self.shooting = shooting
        self.defense = defense
        self.passing = passing
        self.speed = speed
        self.stamina = stamina
        self.memory = memory
        self.skills = skills

    @classmethod
    def from_markdown(cls, profile_dir: str, name: str, stats: dict = None):
        if stats is None:
            stats = {}
            
        mem_path = os.path.join(profile_dir, "memory.md")
        skills_path = os.path.join(profile_dir, "skills.md")
        
        mem = ""
        ski = ""
        
        if profile_dir and os.path.exists(mem_path):
            with open(mem_path, "r", encoding="utf-8", errors="replace") as f:
                mem = f.read().strip()[:250]
                
        if profile_dir and os.path.exists(skills_path):
            with open(skills_path, "r", encoding="utf-8", errors="replace") as f:
                ski = f.read().strip()[:250]
                
        return cls(
            name=name,
            shooting=stats.get("shooting", 75),
            defense=stats.get("defense", 75),
            passing=stats.get("passing", 75),
            speed=stats.get("speed", 75),
            stamina=stats.get("stamina", 75),
            memory=mem,
            skills=ski
        )

    def to_prompt_string(self) -> str:
        stats = (
            f"投={self.shooting:.0f} "
            f"守={self.defense:.0f} "
            f"傳={self.passing:.0f} "
            f"速={self.speed:.0f} "
            f"耐={self.stamina:.0f}"
        )
        profile_parts = [f"【{self.name}】{stats}"]
        if self.memory:
            profile_parts.append(f"背景：{self.memory}")
        if self.skills:
            profile_parts.append(f"技能：{self.skills}")
        return " | ".join(profile_parts)
