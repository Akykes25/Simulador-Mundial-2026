"""Player dataclass for WC2026 simulator."""

from dataclasses import dataclass, field


@dataclass
class Player:
    name: str
    team: str
    position: str              # GK, DEF, MID, FWD
    age: int = 25
    goals_per_game: float = 0.0
    assists_per_game: float = 0.0
    games_played: int = 0      # last 5 seasons
    trophies: int = 0
    market_value_m: float = 0.0  # €M
    fitness: float = 1.0       # 0-1 (1 = fully fit)
    is_injured: bool = False
    form_score: float = 50.0   # 0-100

    @property
    def quality_score(self) -> float:
        """Composite quality score 0-100."""
        base = (
            self.goals_per_game * 20
            + self.assists_per_game * 12
            + min(self.trophies * 3, 20)
            + min(self.market_value_m * 0.05, 20)
            + self.form_score * 0.2
        )
        if self.is_injured:
            base *= 0.0
        else:
            base *= self.fitness
        return min(float(base), 100.0)

    def __repr__(self) -> str:
        return (
            f"Player({self.name}, {self.team}, {self.position}, "
            f"QS={self.quality_score:.1f})"
        )
