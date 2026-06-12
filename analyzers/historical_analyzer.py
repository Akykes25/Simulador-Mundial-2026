"""
analyzers/historical_analyzer.py
Computes H2H advantages from historical match records.
"""
from __future__ import annotations
from fetchers.historical_data import get_h2h, get_h2h_advantage


def compute_h2h_score(team_a: str, team_b: str) -> Dict[str, float]:
    """
    Return H2H performance modifiers for both teams based on historical record.
    Returns {"score_a": float, "score_b": float} where 1.0 = neutral.
    """
    advantage = get_h2h_advantage(team_a, team_b)
    # advantage is -1 to +1 (positive = team_a historically stronger)
    # Convert to modifiers around 1.0 (max ±5%)
    mod_a = 1.0 + advantage * 0.05
    mod_b = 1.0 - advantage * 0.05
    return {
        "mod_a": round(max(0.90, min(1.10, mod_a)), 4),
        "mod_b": round(max(0.90, min(1.10, mod_b)), 4),
        "advantage": round(advantage, 4),
    }


def get_h2h_summary(team_a: str, team_b: str) -> str:
    """Return a human-readable H2H summary."""
    rec = get_h2h(team_a, team_b)
    total = rec["total"]
    if total == 0:
        return f"{team_a} vs {team_b}: No historical data"
    wa = rec["wins_a"]
    wb = rec["wins_b"]
    d = rec["draws"]
    pct_a = (wa + 0.5 * d) / total * 100
    leader = team_a if wa > wb else (team_b if wb > wa else "Even")
    return (
        f"{team_a} vs {team_b}: {wa}W-{d}D-{wb}L "
        f"({pct_a:.0f}% {team_a} advantage) — historical leader: {leader}"
    )


# Needed for the type hint
from typing import Dict
