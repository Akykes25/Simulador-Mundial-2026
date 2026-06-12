"""
fetchers/news_scraper.py
Scrapes sports news portals for player injuries and team conflicts.
Falls back to hardcoded recent news data if scraping fails.
"""
from __future__ import annotations
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from config import ESPN_SOCCER_URL, REQUEST_HEADERS, REQUEST_TIMEOUT

# Hardcoded known injury/conflict data (as of early 2026)
FALLBACK_NEWS: Dict[str, dict] = {
    "Argentina": {
        "injuries": ["Lionel Messi (knee concern, limited training)"],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.10,
        "notes": "Messi managing fitness carefully for final World Cup.",
    },
    "France": {
        "injuries": [],
        "conflicts": ["Reported dressing room tensions between Mbappe and some veterans"],
        "conflict_score": 0.20,
        "injury_score": 0.0,
        "notes": "Internal dynamics post-Deschamps era under scrutiny.",
    },
    "Spain": {
        "injuries": ["Rodri (returning from long injury, not 100%)"],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.08,
        "notes": "Rodri's fitness is key; Lamine Yamal at peak form.",
    },
    "England": {
        "injuries": [],
        "conflicts": ["Media pressure extremely high after Euro 2024 near-miss"],
        "conflict_score": 0.10,
        "injury_score": 0.0,
        "notes": "Strong squad, high expectation pressure.",
    },
    "Brazil": {
        "injuries": [],
        "conflicts": ["Political disputes within CBF affecting morale"],
        "conflict_score": 0.15,
        "injury_score": 0.0,
        "notes": "Brazil seeking redemption after WC2022 QF exit.",
    },
    "Germany": {
        "injuries": ["Manuel Neuer (age-related risk)"],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.05,
        "notes": "Young core with Musiala and Wirtz is exciting.",
    },
    "Portugal": {
        "injuries": ["Cristiano Ronaldo (managing workload at 41)"],
        "conflicts": ["Ronaldo vs younger generation leadership debate"],
        "conflict_score": 0.25,
        "injury_score": 0.12,
        "notes": "Ronaldo's role as leader vs squad depth tension.",
    },
    "Croatia": {
        "injuries": ["Luka Modric (age-related fitness)"],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.10,
        "notes": "Golden generation aging out — transition squad.",
    },
    "Belgium": {
        "injuries": ["Kevin De Bruyne (recurring muscular issues)"],
        "conflicts": ["Post-golden-generation transition angst"],
        "conflict_score": 0.15,
        "injury_score": 0.12,
        "notes": "Belgium rebuilding around Openda and Trossard.",
    },
    "Uruguay": {
        "injuries": [],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.0,
        "notes": "Uruguay garra charrua spirit — dangerous team.",
    },
    "USA": {
        "injuries": ["Tyler Adams (returning from injury)"],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.05,
        "notes": "Host nation, huge crowd advantage.",
    },
    "Mexico": {
        "injuries": ["Guillermo Ochoa (aging GK)"],
        "conflicts": [],
        "conflict_score": 0.08,
        "injury_score": 0.05,
        "notes": "Host nation pressure, desperate to advance past Round of 16.",
    },
    "Canada": {
        "injuries": [],
        "conflicts": [],
        "conflict_score": 0.02,
        "injury_score": 0.0,
        "notes": "Host nation, best generation in history.",
    },
    "Iran": {
        "injuries": [],
        "conflicts": ["Political pressure from government on players"],
        "conflict_score": 0.30,
        "injury_score": 0.0,
        "notes": "Players under political scrutiny.",
    },
    "Poland": {
        "injuries": ["Robert Lewandowski (managing age at 38)"],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.05,
        "notes": "Lewandowski still lethal but aging.",
    },
    "Colombia": {
        "injuries": [],
        "conflicts": [],
        "conflict_score": 0.05,
        "injury_score": 0.0,
        "notes": "Dark horse candidate after Copa America 2024 final.",
    },
    "Serbia": {
        "injuries": [],
        "conflicts": ["Internal tensions over political identity"],
        "conflict_score": 0.20,
        "injury_score": 0.0,
        "notes": "Vlahovic and Milinković-Savić strong but team unity issues.",
    },
    "Nigeria": {
        "injuries": [],
        "conflicts": ["NFF administrative problems affecting preparation"],
        "conflict_score": 0.20,
        "injury_score": 0.0,
        "notes": "Super Eagles talented but organizationally challenged.",
    },
    "Cameroon": {
        "injuries": [],
        "conflicts": ["Ongoing FecaFoot political disputes"],
        "conflict_score": 0.25,
        "injury_score": 0.0,
        "notes": "Administration issues a recurring problem.",
    },
}

_DEFAULT_NEWS = {
    "injuries": [],
    "conflicts": [],
    "conflict_score": 0.05,
    "injury_score": 0.0,
    "notes": "No significant news.",
}


def _scrape_espn_injuries(team_name: str) -> dict:
    """Attempt to scrape ESPN for injury news. Returns empty dict on failure."""
    try:
        url = f"{ESPN_SOCCER_URL}injuries"
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        injuries = []
        for item in soup.find_all("td", class_="col-name")[:50]:
            text = item.get_text(strip=True)
            if team_name.lower() in text.lower():
                injuries.append(text)
        return {"injuries": injuries} if injuries else {}
    except Exception:
        return {}


def fetch_team_news(team_name: str) -> dict:
    """
    Return injury and conflict data for a team.
    Tries live scraping first, falls back to hardcoded data.
    """
    live = _scrape_espn_injuries(team_name)
    base = dict(FALLBACK_NEWS.get(team_name, _DEFAULT_NEWS))
    if live.get("injuries"):
        base["injuries"] = list(set(base["injuries"] + live["injuries"]))
    return base


def fetch_all_news() -> Dict[str, dict]:
    """Fetch news for all teams using fallback data (fast, reliable)."""
    from config import FALLBACK_FIFA_RANKINGS
    result = {}
    for team in FALLBACK_FIFA_RANKINGS:
        result[team] = FALLBACK_NEWS.get(team, dict(_DEFAULT_NEWS))
    return result
