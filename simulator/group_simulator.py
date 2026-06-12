"""
simulator/group_simulator.py
Simulates the group stage of WC2026 (12 groups, each 4 teams, round-robin).
Top 2 from each group advance to Round of 32.
"""
from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np

from models.team import Team
from models.match import MatchResult, MatchContext
from simulator.match_simulator import simulate_match
from fetchers.weather_data import get_weather_modifier
from analyzers.psychological_analyzer import get_psychological_modifier


def _make_standings(teams: List[Team]) -> List[Dict]:
    """Initialize standings for a group."""
    return [
        {
            "team": t,
            "pts": 0, "gp": 0, "w": 0, "d": 0, "l": 0,
            "gf": 0, "ga": 0, "gd": 0,
        }
        for t in teams
    ]


def _update_standings(standings: List[Dict], result: MatchResult) -> None:
    """Update standings dict based on a match result."""
    sa = next(s for s in standings if s["team"] == result.team_a)
    sb = next(s for s in standings if s["team"] == result.team_b)

    sa["gp"] += 1; sb["gp"] += 1
    sa["gf"] += result.goals_a; sa["ga"] += result.goals_b
    sb["gf"] += result.goals_b; sb["ga"] += result.goals_a
    sa["gd"] = sa["gf"] - sa["ga"]
    sb["gd"] = sb["gf"] - sb["ga"]

    if result.goals_a > result.goals_b:
        sa["pts"] += 3; sa["w"] += 1; sb["l"] += 1
    elif result.goals_b > result.goals_a:
        sb["pts"] += 3; sb["w"] += 1; sa["l"] += 1
    else:
        sa["pts"] += 1; sa["d"] += 1
        sb["pts"] += 1; sb["d"] += 1


def sort_standings(standings: List[Dict]) -> List[Dict]:
    """Sort standings by: pts → gd → gf → team strength."""
    return sorted(
        standings,
        key=lambda s: (
            s["pts"],
            s["gd"],
            s["gf"],
            s["team"].overall_strength,
        ),
        reverse=True,
    )


def simulate_group(
    group_name: str,
    teams: List[Team],
    venue: str = "Dallas",
    venue_country: str = "USA",
) -> Tuple[List[Dict], List[MatchResult]]:
    """
    Simulate a complete group stage (6 matches, round-robin).
    Returns (sorted_standings, list_of_results).
    """
    standings = _make_standings(teams)
    results = []

    context = MatchContext(
        venue=venue,
        country=venue_country,
        stage="group",
        is_neutral=True,
    )

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            ta = teams[i]
            tb = teams[j]
            weather = get_weather_modifier(venue, ta.name, tb.name)
            psych = get_psychological_modifier(ta.name, tb.name, venue_country, "group")
            result = simulate_match(ta, tb, context=context, knockout=False,
                                    weather_mod=weather, psych_mod=psych)
            _update_standings(standings, result)
            results.append(result)

    sorted_standings = sort_standings(standings)
    return sorted_standings, results


def simulate_all_groups(
    groups: Dict[str, List[Team]],
) -> Tuple[Dict[str, List[Dict]], Dict[str, List[MatchResult]]]:
    """
    Simulate all 12 groups.
    Returns (all_standings, all_results) both keyed by group name.
    """
    all_standings: Dict[str, List[Dict]] = {}
    all_results: Dict[str, List[MatchResult]] = {}

    venue_assignments = {
        "A": ("New York", "USA"), "B": ("Dallas", "USA"),
        "C": ("Los Angeles", "USA"), "D": ("Miami", "USA"),
        "E": ("Atlanta", "USA"), "F": ("Houston", "USA"),
        "G": ("Seattle", "USA"), "H": ("Kansas City", "USA"),
        "I": ("Boston", "USA"), "J": ("Philadelphia", "USA"),
        "K": ("Guadalajara", "Mexico"), "L": ("Monterrey", "Mexico"),
    }

    for group_name, teams in groups.items():
        venue, country = venue_assignments.get(group_name, ("Dallas", "USA"))
        standings, results = simulate_group(group_name, teams, venue=venue, venue_country=country)
        all_standings[group_name] = standings
        all_results[group_name] = results

    return all_standings, all_results


def get_qualifiers(all_standings: Dict[str, List[Dict]]) -> Tuple[List[Team], List[Team]]:
    """
    Return (group_winners, group_runners_up) from all group standings.
    """
    winners = [standings[0]["team"] for standings in all_standings.values()]
    runners_up = [standings[1]["team"] for standings in all_standings.values()]
    return winners, runners_up
