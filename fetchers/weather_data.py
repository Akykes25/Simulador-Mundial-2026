"""
fetchers/weather_data.py
Returns venue weather conditions for WC2026 matches.
"""
from __future__ import annotations
from typing import Dict
from config import VENUES


def get_venue_conditions(venue: str) -> Dict:
    """Return weather/altitude conditions for a given venue."""
    return VENUES.get(venue, {
        "country": "USA",
        "city": venue,
        "temp_c": 28,
        "humidity": 55,
        "altitude_m": 0,
    })


def get_weather_modifier(venue: str, team_a: str, team_b: str) -> Dict[str, float]:
    """
    Compute performance modifiers based on weather/altitude for each team.
    Returns {"modifier_a": float, "modifier_b": float} where 1.0 = no effect.
    """
    from config import ALTITUDE_THRESHOLD_M, ALTITUDE_PENALTY_NON_ADAPTED, ALTITUDE_ADAPTED_TEAMS

    conditions = get_venue_conditions(venue)
    temp = conditions.get("temp_c", 25)
    humidity = conditions.get("humidity", 50)
    altitude = conditions.get("altitude_m", 0)

    # Heat/humidity penalty (affects all teams equally above 33°C + high humidity)
    heat_index = temp + (humidity - 40) * 0.1
    heat_penalty = 0.0
    if heat_index > 38:
        heat_penalty = 0.03
    elif heat_index > 35:
        heat_penalty = 0.015

    mod_a = 1.0 - heat_penalty
    mod_b = 1.0 - heat_penalty

    # Altitude penalty for non-adapted teams
    if altitude > ALTITUDE_THRESHOLD_M:
        if team_a not in ALTITUDE_ADAPTED_TEAMS:
            mod_a -= ALTITUDE_PENALTY_NON_ADAPTED
        if team_b not in ALTITUDE_ADAPTED_TEAMS:
            mod_b -= ALTITUDE_PENALTY_NON_ADAPTED

    return {"modifier_a": round(max(0.85, mod_a), 4), "modifier_b": round(max(0.85, mod_b), 4)}
