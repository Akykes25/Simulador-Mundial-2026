"""
analyzers/psychological_analyzer.py
Models psychological and political factors that influence match outcomes.
"""
from __future__ import annotations
from typing import Dict, Tuple
from config import POLITICAL_CONFLICTS, HOST_TEAMS, HOST_ADVANTAGE_BOOST


def get_political_tension(team_a: str, team_b: str) -> float:
    """
    Return tension score (0-1) between two teams.
    Higher values indicate more psychological friction.
    """
    key = frozenset({team_a, team_b})
    for conflict_key, data in POLITICAL_CONFLICTS.items():
        if conflict_key == key:
            return data["tension"]
    return 0.0


def get_host_advantage(team: str, venue_country: str) -> float:
    """
    Return home crowd multiplier for a team at a given venue country.
    """
    if team in HOST_TEAMS and team == venue_country:
        return HOST_ADVANTAGE_BOOST
    # Partial crowd support for continental neighbours
    if team in HOST_TEAMS:
        return 1.02  # travelling host support
    return 1.0


def get_psychological_modifier(
    team_a: str, team_b: str,
    venue_country: str,
    stage: str
) -> Dict[str, float]:
    """
    Return psychological performance modifiers for both teams.
    Accounts for: political tension, host advantage, stage pressure.

    Returns {"mod_a": float, "mod_b": float} — multipliers around 1.0.
    """
    tension = get_political_tension(team_a, team_b)

    # Political tension slightly hurts the team under more pressure
    # (weaker team usually feels it more; we apply symmetrically but slightly
    # reduce both)
    tension_penalty = tension * 0.04  # max ~4% when tension=1.0
    mod_a = 1.0 - tension_penalty * 0.5
    mod_b = 1.0 - tension_penalty * 0.5

    # Host advantage
    host_mult_a = get_host_advantage(team_a, venue_country)
    host_mult_b = get_host_advantage(team_b, venue_country)
    mod_a *= host_mult_a
    mod_b *= host_mult_b

    # Stage pressure — later rounds amplify quality differences
    stage_boost = {
        "group": 1.0,
        "round_of_32": 1.01,
        "round_of_16": 1.02,
        "qf": 1.03,
        "sf": 1.04,
        "final": 1.05,
    }
    stage_factor = stage_boost.get(stage, 1.0)
    # Better teams benefit slightly more from pressure (experience)
    mod_a *= stage_factor
    mod_b *= stage_factor

    return {
        "mod_a": round(mod_a, 4),
        "mod_b": round(mod_b, 4),
        "tension": tension,
    }


RIVALRY_DESCRIPTIONS: Dict[frozenset, str] = {
    frozenset({"USA", "Iran"}):
        "USA vs Iran — one of the most politically charged matchups in World Cup history. "
        "Players from both sides face enormous external pressure.",
    frozenset({"Argentina", "England"}):
        "Argentina vs England — the Malvinas/Falklands shadow never fully lifts. "
        "Both squads feel the emotional weight.",
    frozenset({"Serbia", "Albania"}):
        "Serbia vs Albania — Kosovo remains unresolved. Players may find the atmosphere explosive.",
    frozenset({"USA", "Mexico"}):
        "USA vs Mexico — El Clasico de CONCACAF. Deep rivalry amplified by host-nation stakes.",
    frozenset({"Iran", "Saudi Arabia"}):
        "Iran vs Saudi Arabia — regional Middle East tension meets World Cup football.",
}


def describe_rivalry(team_a: str, team_b: str) -> str:
    key = frozenset({team_a, team_b})
    return RIVALRY_DESCRIPTIONS.get(key, "")
