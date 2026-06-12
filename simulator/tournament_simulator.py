"""
simulator/tournament_simulator.py
Runs a complete WC2026 tournament simulation (group stage + knockout rounds).
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import random

from models.team import Team
from simulator.group_simulator import simulate_all_groups, get_qualifiers
from simulator.knockout_simulator import (
    simulate_round, get_third_place_qualifiers, build_round_of_32_bracket
)


class TournamentResult:
    """Stores the outcome of one tournament simulation."""

    def __init__(self):
        self.champion: Optional[Team] = None
        self.finalist: Optional[Team] = None
        self.semi_finalists: List[Team] = []
        self.quarter_finalists: List[Team] = []
        self.round_of_16_teams: List[Team] = []
        self.group_standings: Dict = {}

    def __repr__(self) -> str:
        champ = self.champion.name if self.champion else "Unknown"
        return f"TournamentResult(champion={champ})"


def simulate_tournament(
    groups: Dict[str, List[Team]],
) -> TournamentResult:
    """
    Run one full WC2026 tournament simulation.
    Returns a TournamentResult with champion and detailed advancement info.
    """
    result = TournamentResult()

    # ── Group Stage ────────────────────────────────────────────────────────────
    all_standings, _ = simulate_all_groups(groups)
    result.group_standings = all_standings

    winners, runners_up = get_qualifiers(all_standings)
    third_placed = get_third_place_qualifiers(all_standings, count=8)

    # ── Round of 32 ─────────────────────────────────────────────────────────────
    r32_bracket = build_round_of_32_bracket(winners, runners_up, third_placed)

    # Ensure we have exactly 32 teams (pad with random if needed)
    while len(r32_bracket) < 32:
        r32_bracket.append(random.choice(r32_bracket))
    r32_bracket = r32_bracket[:32]

    r16_teams, _ = simulate_round(r32_bracket, stage="round_of_32")
    result.round_of_16_teams = list(r16_teams)

    # ── Round of 16 ─────────────────────────────────────────────────────────────
    qf_teams, _ = simulate_round(r16_teams, stage="round_of_16")
    result.quarter_finalists = list(qf_teams)

    # ── Quarter-Finals ──────────────────────────────────────────────────────────
    sf_teams, _ = simulate_round(qf_teams, stage="qf")
    result.semi_finalists = list(sf_teams)

    # ── Semi-Finals ─────────────────────────────────────────────────────────────
    finalists, _ = simulate_round(sf_teams, stage="sf")

    # ── Final ───────────────────────────────────────────────────────────────────
    final_result = simulate_round(finalists, stage="final")
    champions = final_result[0]

    result.champion = champions[0]
    result.finalist = finalists[1] if len(finalists) > 1 else finalists[0]
    # Identify the actual finalist (the one who lost)
    if result.champion == finalists[0]:
        result.finalist = finalists[1]
    else:
        result.finalist = finalists[0]

    return result
