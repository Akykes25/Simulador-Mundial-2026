"""
analyzers/player_analyzer.py
Analyzes individual player quality and detects injury impacts.
"""
from __future__ import annotations
from typing import List, Dict
from models.player import Player


def score_player(player: Player) -> float:
    """Return a composite quality score for a single player (0-100)."""
    return player.quality_score


def get_squad_attack_rating(players: List[Player]) -> float:
    """Average quality of attacking players."""
    attackers = [p for p in players if p.position in ("FWD",) and not p.is_injured]
    if not attackers:
        attackers = [p for p in players if not p.is_injured]
    if not attackers:
        return 50.0
    return sum(p.quality_score for p in attackers) / len(attackers)


def get_squad_defense_rating(players: List[Player]) -> float:
    """Average quality of defensive players."""
    defenders = [p for p in players if p.position in ("DEF", "GK") and not p.is_injured]
    if not defenders:
        return 50.0
    return sum(p.quality_score for p in defenders) / len(defenders)


def get_squad_midfield_rating(players: List[Player]) -> float:
    """Average quality of midfield players."""
    mids = [p for p in players if p.position == "MID" and not p.is_injured]
    if not mids:
        return 50.0
    return sum(p.quality_score for p in mids) / len(mids)


def compute_injury_impact(players: List[Player]) -> float:
    """
    Return a multiplier (0.7-1.0) based on how many/quality of injured players.
    More or higher-quality injuries = lower multiplier.
    """
    injured = [p for p in players if p.is_injured]
    if not injured:
        return 1.0
    total_quality_lost = sum(p.market_value_m for p in injured)
    total_quality = sum(p.market_value_m for p in players) or 1.0
    impact_ratio = total_quality_lost / total_quality
    return max(0.70, 1.0 - impact_ratio * 0.5)


def analyze_squad(players: List[Player]) -> Dict[str, float]:
    """Return a full squad analysis dict."""
    return {
        "attack_rating":    round(get_squad_attack_rating(players), 2),
        "defense_rating":   round(get_squad_defense_rating(players), 2),
        "midfield_rating":  round(get_squad_midfield_rating(players), 2),
        "injury_impact":    round(compute_injury_impact(players), 4),
        "overall_quality":  round(
            sum(p.quality_score for p in players if not p.is_injured) / max(1, len([p for p in players if not p.is_injured])),
            2
        ),
    }
