"""Team dataclass for WC2026 simulator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from models.player import Player


@dataclass
class Team:
    name: str
    fifa_code: str
    fifa_points: float
    fifa_rank: int
    confederation: str
    is_host: bool = False

    # Computed / fetched attributes
    recent_form: float = 50.0           # 0-100, last 5 years
    attack_strength: float = 1.0        # avg goals scored per game (normalised)
    defense_strength: float = 1.0       # avg goals conceded per game (normalised, lower = better)
    player_quality_score: float = 50.0  # avg quality of top 23 players
    home_advantage_multiplier: float = 1.0
    key_players: List[Player] = field(default_factory=list)
    injuries: List[Player] = field(default_factory=list)
    internal_conflicts: float = 0.0     # 0-1
    psychological_pressure: float = 0.0 # 0-1

    # Derived — set by team_analyzer
    overall_strength: float = 0.0       # 0-100

    @property
    def injured_key_player_count(self) -> int:
        return sum(1 for p in self.key_players if p.is_injured)

    @property
    def injury_penalty(self) -> float:
        """Returns a multiplier < 1.0 representing injury impact."""
        penalty_per_player = 0.03
        return max(0.7, 1.0 - self.injured_key_player_count * penalty_per_player)

    def __repr__(self) -> str:
        return (
            f"Team({self.name}, rank={self.fifa_rank}, "
            f"strength={self.overall_strength:.1f})"
        )

    def __hash__(self) -> int:
        return hash(self.fifa_code)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Team):
            return self.fifa_code == other.fifa_code
        return NotImplemented
