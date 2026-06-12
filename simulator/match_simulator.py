"""
simulator/match_simulator.py
Poisson-based match simulation engine.
"""
from __future__ import annotations
import numpy as np
from typing import Optional, TYPE_CHECKING

from config import BASE_LAMBDA, LAMBDA_MIN, LAMBDA_MAX
from models.match import MatchResult, MatchContext, Match

if TYPE_CHECKING:
    from models.team import Team


def _compute_lambda(team_a: "Team", team_b: "Team") -> tuple[float, float]:
    """
    Compute Poisson lambda (expected goals) for each team using:
    - Attack strength vs opponent defense strength
    - Overall strength ratio
    - Home advantage & injury penalty
    """
    str_a = max(team_a.overall_strength, 1.0)
    str_b = max(team_b.overall_strength, 1.0)

    ratio = str_a / str_b
    ratio_b = str_b / str_a

    atk_a = max(team_a.attack_strength, 0.3)
    def_b = max(team_b.defense_strength, 0.3)
    atk_b = max(team_b.attack_strength, 0.3)
    def_a = max(team_a.defense_strength, 0.3)

    raw_a = atk_a / def_b * BASE_LAMBDA
    raw_b = atk_b / def_a * BASE_LAMBDA

    lambda_a = raw_a * (ratio ** 0.4) * team_a.home_advantage_multiplier * team_a.injury_penalty
    lambda_b = raw_b * (ratio_b ** 0.4) * team_b.home_advantage_multiplier * team_b.injury_penalty

    lambda_a = float(np.clip(lambda_a, LAMBDA_MIN, LAMBDA_MAX))
    lambda_b = float(np.clip(lambda_b, LAMBDA_MIN, LAMBDA_MAX))

    return lambda_a, lambda_b


def simulate_match(
    team_a: "Team",
    team_b: "Team",
    context: Optional[MatchContext] = None,
    knockout: bool = False,
    weather_mod: Optional[dict] = None,
    psych_mod: Optional[dict] = None,
) -> MatchResult:
    """
    Simulate a single match between team_a and team_b.
    Returns a MatchResult with goals and optional penalty winner.
    """
    if context is None:
        context = MatchContext()

    lambda_a, lambda_b = _compute_lambda(team_a, team_b)

    # Apply weather modifier
    if weather_mod:
        lambda_a *= weather_mod.get("modifier_a", 1.0)
        lambda_b *= weather_mod.get("modifier_b", 1.0)

    # Apply psychological modifier
    if psych_mod:
        lambda_a *= psych_mod.get("mod_a", 1.0)
        lambda_b *= psych_mod.get("mod_b", 1.0)

    # Apply internal conflict penalty
    conflict_pen_a = 1.0 - team_a.internal_conflicts * 0.10
    conflict_pen_b = 1.0 - team_b.internal_conflicts * 0.10
    lambda_a *= max(0.85, conflict_pen_a)
    lambda_b *= max(0.85, conflict_pen_b)

    lambda_a = float(np.clip(lambda_a, LAMBDA_MIN, LAMBDA_MAX))
    lambda_b = float(np.clip(lambda_b, LAMBDA_MIN, LAMBDA_MAX))

    goals_a = int(np.random.poisson(lambda_a))
    goals_b = int(np.random.poisson(lambda_b))

    # Determine winner in regulation
    if goals_a > goals_b:
        winner = team_a
    elif goals_b > goals_a:
        winner = team_b
    else:
        winner = None  # draw

    went_to_extra_time = False
    went_to_penalties = False
    penalty_winner = None

    if knockout and winner is None:
        # Extra time — re-draw with slightly reduced lambdas
        went_to_extra_time = True
        et_a = int(np.random.poisson(lambda_a * 0.4))
        et_b = int(np.random.poisson(lambda_b * 0.4))
        goals_a += et_a
        goals_b += et_b

        if goals_a > goals_b:
            winner = team_a
        elif goals_b > goals_a:
            winner = team_b
        else:
            # Penalty shootout
            went_to_penalties = True
            str_a = team_a.overall_strength
            str_b = team_b.overall_strength
            pen_prob_a = str_a / (str_a + str_b)
            penalty_winner = team_a if np.random.random() < pen_prob_a else team_b
            winner = penalty_winner

    return MatchResult(
        team_a=team_a,
        team_b=team_b,
        goals_a=goals_a,
        goals_b=goals_b,
        winner=winner,
        went_to_extra_time=went_to_extra_time,
        went_to_penalties=went_to_penalties,
        penalty_winner=penalty_winner,
    )
