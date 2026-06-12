"""Match and MatchResult dataclasses for WC2026 simulator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.team import Team


@dataclass
class MatchContext:
    """Environmental and contextual factors for a match."""
    venue: str = "Unknown"
    country: str = "USA"
    temp_c: float = 25.0
    humidity_pct: float = 50.0
    altitude_m: float = 0.0
    stage: str = "group"        # group | round_of_32 | round_of_16 | qf | sf | final
    is_neutral: bool = True


@dataclass
class MatchResult:
    """Result of a simulated match."""
    team_a: "Team"
    team_b: "Team"
    goals_a: int
    goals_b: int
    winner: Optional["Team"]    # None = draw (only valid in group stage)
    went_to_extra_time: bool = False
    went_to_penalties: bool = False
    penalty_winner: Optional["Team"] = None

    @property
    def effective_winner(self) -> Optional["Team"]:
        """In knockout rounds, returns the penalty winner if applicable."""
        if self.penalty_winner:
            return self.penalty_winner
        return self.winner


@dataclass
class Match:
    """Represents a scheduled or completed match."""
    team_a: "Team"
    team_b: "Team"
    context: MatchContext = field(default_factory=MatchContext)
    result: Optional[MatchResult] = None

    def __repr__(self) -> str:
        a = self.team_a.name
        b = self.team_b.name
        if self.result:
            return f"Match({a} {self.result.goals_a}-{self.result.goals_b} {b})"
        return f"Match({a} vs {b})"
