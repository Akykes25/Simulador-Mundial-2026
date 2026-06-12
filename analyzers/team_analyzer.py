"""
analyzers/team_analyzer.py
Builds Team objects with computed strength scores from all data sources.
"""
from __future__ import annotations
import json
import os
from typing import Dict, List

from config import (
    FALLBACK_FIFA_RANKINGS,
    WEIGHT_FIFA_RANKING, WEIGHT_RECENT_FORM, WEIGHT_PLAYER_QUALITY,
    HOST_TEAMS,
)
from models.team import Team
from models.player import Player
from fetchers.player_stats import fetch_player_stats
from fetchers.news_scraper import fetch_team_news


def _normalize_fifa(points: float, max_pts: float = 1900.0, min_pts: float = 700.0) -> float:
    """Normalize FIFA points to 0-100 scale."""
    return max(0.0, min(100.0, (points - min_pts) / (max_pts - min_pts) * 100.0))


def _compute_player_quality(players: List[Player]) -> float:
    """Average quality score of the squad's top players."""
    if not players:
        return 50.0
    scores = [p.quality_score for p in players]
    return sum(scores) / len(scores)


def _estimate_recent_form(team_name: str, fifa_points: float) -> float:
    """
    Estimate recent form score (0-100) based on FIFA points + known 2025 performance.
    Teams with high FIFA ranking but known poor recent run get penalized.
    """
    form_overrides = {
        "Argentina":   88.0,  # Copa America 2024 winner, WC2022 champion
        "France":      85.0,  # Strong recent run
        "Spain":       90.0,  # Euro 2024 winner
        "England":     82.0,  # Good form but no major trophy
        "Brazil":      78.0,  # Struggled in recent WC qualifiers
        "Portugal":    80.0,  # Good form, Ronaldo era ending
        "Netherlands": 80.0,  # Euro 2024 SF
        "Germany":     82.0,  # Home Euro 2024 QF, rebuilding well
        "Morocco":     78.0,  # WC2022 semi-finalists, AFCON ambitions
        "Belgium":     70.0,  # End of golden generation
        "Japan":       80.0,  # Strong Asian Cup, WC2022 R16
        "Croatia":     72.0,  # Aging squad, WC2022 3rd place
        "USA":         72.0,  # Host, improving rapidly
        "Colombia":    82.0,  # Copa America 2024 finalist
        "Mexico":      68.0,  # Host, "quinto partido" pressure
        "Uruguay":     78.0,  # Consistent CONMEBOL performer
        "Switzerland": 76.0,  # Euro 2024 QF
        "Senegal":     72.0,  # AFCON 2021 winner
        "Italy":       72.0,  # Failed to qualify for WC2022, rebuilding
        "Denmark":     74.0,  # Solid but Euro 2024 early exit
        "Ecuador":     70.0,  # Consistent South America
        "South Korea": 73.0,  # WC2022 R16, solid AFC
        "Australia":   68.0,  # WC2022 QF (best ever)
        "Canada":      73.0,  # Host, first WC in 40 years energized them
        "Austria":     72.0,  # Euro 2024 R16
        "Turkey":      73.0,  # Euro 2024 QF
        "Poland":      65.0,  # Euro 2024 group stage exit
        "Ukraine":     65.0,  # War context, reduced preparation
        "Nigeria":     62.0,  # AFCON 2023 runner-up
        "Serbia":      65.0,  # WC2022 group stage exit
        "Iran":        62.0,  # AFC competent but limited top-level experience
        "Chile":       60.0,  # Missed WC2022, rebuilding
        "Saudi Arabia":60.0,  # WC2022 Argentina win — outlier performance
        "Romania":     63.0,  # Euro 2024 R16
        "Hungary":     60.0,  # Euro 2024 group stage
        "Czech Republic":60.0,
        "Albania":     58.0,  # Euro 2024 group stage
        "Slovakia":    62.0,  # Euro 2024 R16
        "Scotland":    60.0,  # Euro 2024 group stage
        "Venezuela":   58.0,  # Best WC qualification campaign
        "Paraguay":    55.0,
        "Bolivia":     50.0,
        "South Africa":55.0,
        "Egypt":       58.0,  # AFCON finalist
        "Cameroon":    52.0,
        "DR Congo":    55.0,  # AFCON 2024 finalist
        "Panama":      55.0,
        "Honduras":    50.0,
        "Costa Rica":  55.0,
        "Jamaica":     52.0,
        "Slovenia":    60.0,  # Euro 2024 R16
        "Georgia":     60.0,  # Surprise Euro 2024 R16
        "Jordan":      55.0,  # AFC runner-up
        "Qatar":       50.0,  # WC2022 host — poor performance
        "Uzbekistan":  55.0,  # Best AFC run
        "New Zealand": 50.0,
        "Kenya":       48.0,
        "Ghana":       55.0,
        "Peru":        52.0,
    }
    return form_overrides.get(team_name, _normalize_fifa(fifa_points))


def _compute_attack_strength(players: List[Player]) -> float:
    """Estimate avg goals per game from squad's forwards."""
    forwards = [p for p in players if p.position in ("FWD", "MID")]
    if not forwards:
        return 1.0
    avg_gpg = sum(p.goals_per_game for p in forwards) / len(forwards)
    # Normalise: 0.4 gpg per player ~ 1.5 team goals/game → strength ~1.5
    return min(3.0, max(0.4, avg_gpg * 4))


def _compute_defense_strength(players: List[Player]) -> float:
    """Estimate defensive quality. Lower = better (goals conceded rate)."""
    defenders = [p for p in players if p.position in ("DEF", "GK")]
    if not defenders:
        return 1.2
    avg_form = sum(p.form_score for p in defenders) / len(defenders)
    # 90 form → 0.7 goals conceded; 50 form → 1.5
    return round(max(0.5, 1.8 - (avg_form / 100) * 1.3), 3)


def build_team(team_name: str, rankings: Dict | None = None) -> Team:
    """
    Build a fully populated Team object from all available data sources.
    """
    if rankings is None:
        rankings = FALLBACK_FIFA_RANKINGS

    rank_data = rankings.get(team_name, {
        "points": 800.0, "rank": 50, "confederation": "UEFA"
    })
    fifa_points = rank_data["points"]
    fifa_rank = rank_data["rank"]
    confederation = rank_data["confederation"]

    players = fetch_player_stats(team_name, quality_fallback=_normalize_fifa(fifa_points))
    news = fetch_team_news(team_name)

    # Mark injured players
    injury_names = [inj.split("(")[0].strip() for inj in news.get("injuries", [])]
    for p in players:
        if any(name in p.name for name in injury_names):
            p.is_injured = True
            p.fitness = 0.5

    recent_form = _estimate_recent_form(team_name, fifa_points)
    player_quality = _compute_player_quality(players)
    attack_str = _compute_attack_strength(players)
    defense_str = _compute_defense_strength(players)

    # Composite strength (0-100)
    normalized_rank = _normalize_fifa(fifa_points)
    overall = (
        normalized_rank * WEIGHT_FIFA_RANKING
        + recent_form * WEIGHT_RECENT_FORM
        + player_quality * WEIGHT_PLAYER_QUALITY
        + 0.0  # H2H and context added in match simulation
    ) / (WEIGHT_FIFA_RANKING + WEIGHT_RECENT_FORM + WEIGHT_PLAYER_QUALITY)

    team = Team(
        name=team_name,
        fifa_code=team_name[:3].upper(),
        fifa_points=fifa_points,
        fifa_rank=fifa_rank,
        confederation=confederation,
        is_host=(team_name in HOST_TEAMS),
        recent_form=recent_form,
        attack_strength=attack_str,
        defense_strength=defense_str,
        player_quality_score=player_quality,
        home_advantage_multiplier=1.05 if team_name in HOST_TEAMS else 1.0,
        key_players=players,
        injuries=[p for p in players if p.is_injured],
        internal_conflicts=news.get("conflict_score", 0.05),
        psychological_pressure=0.1 if team_name in HOST_TEAMS else 0.05,
        overall_strength=round(overall, 2),
    )
    return team


def build_all_teams(rankings: Dict | None = None) -> Dict[str, Team]:
    """Build Team objects for all 48 WC2026 participants."""
    if rankings is None:
        rankings = FALLBACK_FIFA_RANKINGS
    return {name: build_team(name, rankings) for name in rankings}
