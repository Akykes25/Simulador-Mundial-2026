"""
fetchers/historical_data.py
Provides head-to-head (H2H) historical match data between national teams.
"""
from __future__ import annotations
from typing import Dict, Tuple

# H2H records: (team_a, team_b) -> {"wins_a": int, "wins_b": int, "draws": int, "total": int}
# All data from last 20+ years of competitive and friendly matches.
# Key: frozenset so order doesn't matter; value keyed by first team alphabetically.

_H2H_RAW: Dict[Tuple[str, str], Dict] = {
    ("Argentina", "Brazil"):       {"wins_a": 48, "wins_b": 42, "draws": 26, "total": 116},
    ("Argentina", "England"):      {"wins_a": 13, "wins_b": 7,  "draws": 5,  "total": 25},
    ("Argentina", "France"):       {"wins_a": 4,  "wins_b": 3,  "draws": 1,  "total": 8},
    ("Argentina", "Germany"):      {"wins_a": 8,  "wins_b": 8,  "draws": 4,  "total": 20},
    ("Argentina", "Netherlands"):  {"wins_a": 6,  "wins_b": 5,  "draws": 3,  "total": 14},
    ("Argentina", "Uruguay"):      {"wins_a": 62, "wins_b": 55, "draws": 28, "total": 145},
    ("Argentina", "Colombia"):     {"wins_a": 15, "wins_b": 6,  "draws": 8,  "total": 29},
    ("Argentina", "Ecuador"):      {"wins_a": 23, "wins_b": 4,  "draws": 10, "total": 37},
    ("Argentina", "Chile"):        {"wins_a": 55, "wins_b": 17, "draws": 19, "total": 91},
    ("Argentina", "Croatia"):      {"wins_a": 3,  "wins_b": 1,  "draws": 0,  "total": 4},
    ("Brazil", "France"):          {"wins_a": 5,  "wins_b": 3,  "draws": 1,  "total": 9},
    ("Brazil", "Germany"):         {"wins_a": 12, "wins_b": 12, "draws": 5,  "total": 29},
    ("Brazil", "England"):         {"wins_a": 11, "wins_b": 5,  "draws": 8,  "total": 24},
    ("Brazil", "Portugal"):        {"wins_a": 7,  "wins_b": 4,  "draws": 4,  "total": 15},
    ("Brazil", "Uruguay"):         {"wins_a": 47, "wins_b": 32, "draws": 22, "total": 101},
    ("Brazil", "Colombia"):        {"wins_a": 19, "wins_b": 7,  "draws": 8,  "total": 34},
    ("Brazil", "Netherlands"):     {"wins_a": 7,  "wins_b": 6,  "draws": 4,  "total": 17},
    ("Brazil", "Croatia"):         {"wins_a": 5,  "wins_b": 1,  "draws": 2,  "total": 8},
    ("France", "Germany"):         {"wins_a": 17, "wins_b": 16, "draws": 8,  "total": 41},
    ("France", "England"):         {"wins_a": 17, "wins_b": 17, "draws": 6,  "total": 40},
    ("France", "Spain"):           {"wins_a": 19, "wins_b": 18, "draws": 10, "total": 47},
    ("France", "Portugal"):        {"wins_a": 17, "wins_b": 9,  "draws": 9,  "total": 35},
    ("France", "Netherlands"):     {"wins_a": 12, "wins_b": 9,  "draws": 8,  "total": 29},
    ("France", "Croatia"):         {"wins_a": 7,  "wins_b": 2,  "draws": 2,  "total": 11},
    ("France", "Morocco"):         {"wins_a": 5,  "wins_b": 1,  "draws": 1,  "total": 7},
    ("Germany", "England"):        {"wins_a": 22, "wins_b": 14, "draws": 10, "total": 46},
    ("Germany", "Spain"):          {"wins_a": 19, "wins_b": 15, "draws": 8,  "total": 42},
    ("Germany", "Netherlands"):    {"wins_a": 25, "wins_b": 18, "draws": 10, "total": 53},
    ("Germany", "Portugal"):       {"wins_a": 16, "wins_b": 8,  "draws": 6,  "total": 30},
    ("Germany", "Croatia"):        {"wins_a": 5,  "wins_b": 1,  "draws": 3,  "total": 9},
    ("Spain", "England"):          {"wins_a": 16, "wins_b": 15, "draws": 9,  "total": 40},
    ("Spain", "Portugal"):         {"wins_a": 17, "wins_b": 16, "draws": 12, "total": 45},
    ("Spain", "Netherlands"):      {"wins_a": 11, "wins_b": 8,  "draws": 7,  "total": 26},
    ("Spain", "Croatia"):          {"wins_a": 7,  "wins_b": 2,  "draws": 2,  "total": 11},
    ("England", "Netherlands"):    {"wins_a": 10, "wins_b": 8,  "draws": 5,  "total": 23},
    ("England", "Croatia"):        {"wins_a": 7,  "wins_b": 3,  "draws": 2,  "total": 12},
    ("England", "Switzerland"):    {"wins_a": 13, "wins_b": 5,  "draws": 6,  "total": 24},
    ("Netherlands", "Croatia"):    {"wins_a": 6,  "wins_b": 2,  "draws": 3,  "total": 11},
    ("Portugal", "Croatia"):       {"wins_a": 3,  "wins_b": 2,  "draws": 0,  "total": 5},
    ("Uruguay", "Colombia"):       {"wins_a": 12, "wins_b": 8,  "draws": 5,  "total": 25},
    ("Uruguay", "Ecuador"):        {"wins_a": 16, "wins_b": 5,  "draws": 7,  "total": 28},
    ("Uruguay", "Chile"):          {"wins_a": 27, "wins_b": 16, "draws": 10, "total": 53},
    ("Colombia", "Ecuador"):       {"wins_a": 12, "wins_b": 7,  "draws": 8,  "total": 27},
    ("Morocco", "Senegal"):        {"wins_a": 8,  "wins_b": 6,  "draws": 5,  "total": 19},
    ("Morocco", "Nigeria"):        {"wins_a": 4,  "wins_b": 3,  "draws": 2,  "total": 9},
    ("Japan", "South Korea"):      {"wins_a": 13, "wins_b": 42, "draws": 23, "total": 78},
    ("Japan", "Australia"):        {"wins_a": 14, "wins_b": 10, "draws": 7,  "total": 31},
    ("South Korea", "Iran"):       {"wins_a": 8,  "wins_b": 12, "draws": 7,  "total": 27},
    ("USA", "Mexico"):             {"wins_a": 25, "wins_b": 36, "draws": 17, "total": 78},
    ("USA", "Canada"):             {"wins_a": 18, "wins_b": 8,  "draws": 7,  "total": 33},
    ("USA", "Iran"):               {"wins_a": 3,  "wins_b": 1,  "draws": 0,  "total": 4},
    ("Mexico", "Canada"):          {"wins_a": 23, "wins_b": 8,  "draws": 9,  "total": 40},
    ("Mexico", "Costa Rica"):      {"wins_a": 16, "wins_b": 9,  "draws": 8,  "total": 33},
    ("Italy", "Germany"):          {"wins_a": 12, "wins_b": 16, "draws": 14, "total": 42},
    ("Italy", "Spain"):            {"wins_a": 12, "wins_b": 13, "draws": 7,  "total": 32},
    ("Italy", "France"):           {"wins_a": 14, "wins_b": 12, "draws": 11, "total": 37},
    ("Italy", "England"):          {"wins_a": 11, "wins_b": 8,  "draws": 7,  "total": 26},
    ("Italy", "Belgium"):          {"wins_a": 15, "wins_b": 7,  "draws": 6,  "total": 28},
    ("Belgium", "Netherlands"):    {"wins_a": 14, "wins_b": 19, "draws": 11, "total": 44},
    ("Belgium", "France"):         {"wins_a": 9,  "wins_b": 22, "draws": 11, "total": 42},
    ("Belgium", "England"):        {"wins_a": 15, "wins_b": 12, "draws": 7,  "total": 34},
    ("Serbia", "Croatia"):         {"wins_a": 2,  "wins_b": 2,  "draws": 1,  "total": 5},
    ("Iran", "Saudi Arabia"):      {"wins_a": 12, "wins_b": 10, "draws": 7,  "total": 29},
    ("Nigeria", "Senegal"):        {"wins_a": 5,  "wins_b": 4,  "draws": 2,  "total": 11},
    ("Nigeria", "Ghana"):          {"wins_a": 8,  "wins_b": 6,  "draws": 4,  "total": 18},
    ("Nigeria", "Cameroon"):       {"wins_a": 7,  "wins_b": 5,  "draws": 3,  "total": 15},
    ("DR Congo", "Cameroon"):      {"wins_a": 7,  "wins_b": 8,  "draws": 5,  "total": 20},
    ("Saudi Arabia", "Australia"): {"wins_a": 6,  "wins_b": 5,  "draws": 3,  "total": 14},
    ("Ecuador", "Colombia"):       {"wins_a": 7,  "wins_b": 12, "draws": 8,  "total": 27},
    ("Venezuela", "Colombia"):     {"wins_a": 4,  "wins_b": 14, "draws": 8,  "total": 26},
    ("Bolivia", "Peru"):           {"wins_a": 18, "wins_b": 22, "draws": 14, "total": 54},
    ("Australia", "New Zealand"):  {"wins_a": 19, "wins_b": 4,  "draws": 5,  "total": 28},
    ("Turkey", "Serbia"):          {"wins_a": 6,  "wins_b": 7,  "draws": 4,  "total": 17},
    ("Turkey", "Croatia"):         {"wins_a": 3,  "wins_b": 5,  "draws": 2,  "total": 10},
    ("Poland", "Ukraine"):         {"wins_a": 6,  "wins_b": 5,  "draws": 3,  "total": 14},
    ("Romania", "Hungary"):        {"wins_a": 20, "wins_b": 22, "draws": 12, "total": 54},
    ("Czech Republic", "Slovakia"):{"wins_a": 4,  "wins_b": 3,  "draws": 1,  "total": 8},
    ("Albania", "Serbia"):         {"wins_a": 1,  "wins_b": 2,  "draws": 0,  "total": 3},
    ("Scotland", "England"):       {"wins_a": 41, "wins_b": 48, "draws": 24, "total": 113},
    ("Georgia", "Ukraine"):        {"wins_a": 2,  "wins_b": 5,  "draws": 2,  "total": 9},
    ("Jordan", "Saudi Arabia"):    {"wins_a": 5,  "wins_b": 10, "draws": 4,  "total": 19},
    ("Qatar", "Iran"):             {"wins_a": 3,  "wins_b": 7,  "draws": 3,  "total": 13},
    ("Uzbekistan", "Iran"):        {"wins_a": 2,  "wins_b": 6,  "draws": 2,  "total": 10},
    ("Jamaica", "USA"):            {"wins_a": 3,  "wins_b": 8,  "draws": 3,  "total": 14},
    ("Panama", "Costa Rica"):      {"wins_a": 7,  "wins_b": 9,  "draws": 5,  "total": 21},
    ("Honduras", "Panama"):        {"wins_a": 8,  "wins_b": 6,  "draws": 5,  "total": 19},
    ("Chile", "Colombia"):         {"wins_a": 19, "wins_b": 14, "draws": 11, "total": 44},
    ("Chile", "Ecuador"):          {"wins_a": 18, "wins_b": 10, "draws": 10, "total": 38},
    ("Paraguay", "Bolivia"):       {"wins_a": 24, "wins_b": 15, "draws": 12, "total": 51},
    ("Paraguay", "Venezuela"):     {"wins_a": 12, "wins_b": 6,  "draws": 7,  "total": 25},
    ("Peru", "Colombia"):          {"wins_a": 15, "wins_b": 18, "draws": 10, "total": 43},
    ("Peru", "Venezuela"):         {"wins_a": 12, "wins_b": 5,  "draws": 7,  "total": 24},
    ("South Africa", "Nigeria"):   {"wins_a": 4,  "wins_b": 7,  "draws": 2,  "total": 13},
    ("South Africa", "Senegal"):   {"wins_a": 3,  "wins_b": 4,  "draws": 2,  "total": 9},
    ("Egypt", "Cameroon"):         {"wins_a": 6,  "wins_b": 5,  "draws": 3,  "total": 14},
    ("Egypt", "Morocco"):          {"wins_a": 8,  "wins_b": 7,  "draws": 6,  "total": 21},
    ("Ghana", "Cameroon"):         {"wins_a": 5,  "wins_b": 4,  "draws": 3,  "total": 12},
    ("Kenya", "DR Congo"):         {"wins_a": 2,  "wins_b": 5,  "draws": 2,  "total": 9},
    ("New Zealand", "Australia"):  {"wins_a": 4,  "wins_b": 19, "draws": 5,  "total": 28},
    ("Slovenia", "Austria"):       {"wins_a": 3,  "wins_b": 4,  "draws": 2,  "total": 9},
    ("Slovenia", "Croatia"):       {"wins_a": 3,  "wins_b": 4,  "draws": 3,  "total": 10},
}


def get_h2h(team_a: str, team_b: str) -> Dict:
    """
    Return H2H record between two teams.
    wins_a / wins_b correspond to team_a / team_b as passed.
    """
    key = (team_a, team_b)
    rev = (team_b, team_a)
    if key in _H2H_RAW:
        return dict(_H2H_RAW[key])
    elif rev in _H2H_RAW:
        r = _H2H_RAW[rev]
        return {
            "wins_a": r["wins_b"],
            "wins_b": r["wins_a"],
            "draws": r["draws"],
            "total": r["total"],
        }
    else:
        return {"wins_a": 1, "wins_b": 1, "draws": 1, "total": 3}


def get_h2h_advantage(team_a: str, team_b: str) -> float:
    """
    Return a value between -1 and 1 indicating historical advantage.
    Positive = team_a historically stronger, negative = team_b.
    """
    h2h = get_h2h(team_a, team_b)
    total = h2h["total"]
    if total == 0:
        return 0.0
    win_rate_a = (h2h["wins_a"] + 0.5 * h2h["draws"]) / total
    win_rate_b = (h2h["wins_b"] + 0.5 * h2h["draws"]) / total
    return win_rate_a - win_rate_b
