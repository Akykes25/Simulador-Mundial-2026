"""
simulator/knockout_simulator.py
Simulates the knockout rounds of WC2026.
Round of 32 (24 teams from groups + ... actually WC2026 has R32 with 32 teams).

WC2026 format:
- 48 teams in 12 groups of 4
- Top 2 from each group + best 8 third-placed teams = 32 teams in Round of 32
- Then R16, QF, SF, Final
"""
from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np

from models.team import Team
from models.match import MatchResult, MatchContext
from simulator.match_simulator import simulate_match
from fetchers.weather_data import get_weather_modifier
from analyzers.psychological_analyzer import get_psychological_modifier


# Venue list for knockout rounds (rotate through major venues)
_KNOCKOUT_VENUES = [
    ("New York", "USA"), ("Dallas", "USA"), ("Los Angeles", "USA"),
    ("Miami", "USA"), ("Atlanta", "USA"), ("Houston", "USA"),
    ("Seattle", "USA"), ("Kansas City", "USA"),
]
_venue_idx = 0


def _get_next_venue() -> Tuple[str, str]:
    global _venue_idx
    v = _KNOCKOUT_VENUES[_venue_idx % len(_KNOCKOUT_VENUES)]
    _venue_idx += 1
    return v


def simulate_knockout_match(
    team_a: Team,
    team_b: Team,
    stage: str = "round_of_32",
) -> MatchResult:
    """Simulate a single knockout match (always produces a winner)."""
    venue, country = _get_next_venue()
    context = MatchContext(venue=venue, country=country, stage=stage, is_neutral=True)
    weather = get_weather_modifier(venue, team_a.name, team_b.name)
    psych = get_psychological_modifier(team_a.name, team_b.name, country, stage)
    return simulate_match(
        team_a, team_b, context=context, knockout=True,
        weather_mod=weather, psych_mod=psych,
    )


def simulate_round(
    teams: List[Team],
    stage: str,
) -> Tuple[List[Team], List[MatchResult]]:
    """
    Simulate one knockout round. teams must have even length.
    Returns (winners, results).
    Pairs are consecutive: [0 vs 1, 2 vs 3, ...]
    """
    assert len(teams) % 2 == 0, f"Odd number of teams in knockout round: {len(teams)}"
    winners = []
    results = []
    for i in range(0, len(teams), 2):
        ta = teams[i]
        tb = teams[i + 1]
        result = simulate_knockout_match(ta, tb, stage=stage)
        winner = result.effective_winner
        winners.append(winner)
        results.append(result)
    return winners, results


def get_third_place_qualifiers(
    all_standings: dict,
    count: int = 8,
) -> List[Team]:
    """
    Pick the best `count` third-placed teams from all groups.
    Sorted by pts → gd → gf → overall_strength.
    """
    thirds = []
    for group_name, standings in all_standings.items():
        if len(standings) >= 3:
            thirds.append(standings[2])

    thirds_sorted = sorted(
        thirds,
        key=lambda s: (
            s["pts"], s["gd"], s["gf"], s["team"].overall_strength
        ),
        reverse=True,
    )
    return [s["team"] for s in thirds_sorted[:count]]


def build_round_of_32_bracket(
    winners: List[Team],
    runners_up: List[Team],
    third_placed: List[Team],
) -> List[Team]:
    """
    Build R32 bracket from 12 winners + 12 runners-up + 8 best thirds = 32 teams.
    Pairing: winner[i] vs runner_up[j] (avoid same-group clashes where possible).
    Simple implementation: interleave winners and runners-up, add thirds.
    """
    # 12 group winners + 12 group runners-up + 8 best thirds = 32
    # Simple bracket: winner A vs runner B, winner B vs runner A, etc.
    bracket: List[Team] = []

    group_labels = list("ABCDEFGHIJKL")
    # Predefined WC2026-style R32 pairing (simplified)
    # Winners: A,B,C,D,E,F vs Runners-up: B,A,D,C,F,E
    # Then remaining 6 winners vs 6 runners-up + 8 thirds
    paired: List[Team] = []

    winner_pairs = [
        (winners[0], runners_up[1]),   # A vs runner B
        (winners[1], runners_up[0]),   # B vs runner A
        (winners[2], runners_up[3]),   # C vs runner D
        (winners[3], runners_up[2]),   # D vs runner C
        (winners[4], runners_up[5]),   # E vs runner F
        (winners[5], runners_up[4]),   # F vs runner E
        (winners[6], runners_up[7]),   # G vs runner H
        (winners[7], runners_up[6]),   # H vs runner G
        (winners[8], runners_up[9]),   # I vs runner J
        (winners[9], runners_up[8]),   # J vs runner I
        (winners[10], runners_up[11]), # K vs runner L
        (winners[11], runners_up[10]), # L vs runner K
    ]

    # Flatten pairs into bracket order, then add 8 third-placed teams (paired together)
    for w, r in winner_pairs:
        bracket.append(w)
        bracket.append(r)

    # Third-placed teams play each other in 4 matches
    for i in range(0, len(third_placed), 2):
        if i + 1 < len(third_placed):
            bracket.append(third_placed[i])
            bracket.append(third_placed[i + 1])

    # If we have an odd third-placed team, give them a bye (just add them; they'll be handled)
    return bracket[:32]


def run_knockout_bracket(
    qualifiers: List[Team],
) -> Tuple[Team, dict]:
    """
    Run the full knockout bracket from 32 qualifiers to champion.
    Qualifiers should already be in bracket order (seeded 1v32, 2v31...).
    Returns (champion, results_by_stage).
    """
    global _venue_idx
    _venue_idx = 0  # reset venue rotation per tournament

    stage_map = {32: "round_of_32", 16: "round_of_16", 8: "qf", 4: "sf", 2: "final"}
    all_results: dict = {}
    current = list(qualifiers)

    while len(current) > 1:
        n = len(current)
        stage = stage_map.get(n, f"round_{n}")
        winners, results = simulate_round(current, stage)
        all_results[stage] = results
        current = winners

    return current[0], all_results
