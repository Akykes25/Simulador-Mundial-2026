"""
fetchers/fifa_data.py
Fetches FIFA/Elo ratings from eloratings.net with fallback to hardcoded data.
"""

from __future__ import annotations
import json
import os
from typing import Dict

import requests
from bs4 import BeautifulSoup

from config import (
    ELO_RATINGS_URL, REQUEST_HEADERS, REQUEST_TIMEOUT,
    FALLBACK_FIFA_RANKINGS
)


def fetch_elo_ratings() -> Dict[str, dict]:
    """
    Attempt to scrape World Football Elo Ratings.
    Returns a dict: team_name -> {"points": float, "rank": int, "confederation": str}
    Falls back to hardcoded data on any error.
    """
    try:
        resp = requests.get(
            ELO_RATINGS_URL,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        ratings: Dict[str, dict] = {}
        table = soup.find("table", {"id": "t"})
        if table is None:
            raise ValueError("Elo ratings table not found in page")
        rows = table.find_all("tr")[1:]  # skip header
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            rank_text = cells[0].get_text(strip=True)
            name_text = cells[1].get_text(strip=True)
            pts_text = cells[3].get_text(strip=True)
            try:
                rank = int(rank_text)
                pts = float(pts_text)
            except ValueError:
                continue
            # Only keep teams that qualify for WC2026 (use fallback list as filter)
            if name_text in FALLBACK_FIFA_RANKINGS:
                ratings[name_text] = {
                    "points": pts,
                    "rank": rank,
                    "confederation": FALLBACK_FIFA_RANKINGS[name_text]["confederation"]
                }
        if len(ratings) < 30:
            raise ValueError(f"Only got {len(ratings)} teams from scrape — too few")
        return ratings
    except Exception as exc:
        print(f"[fifa_data] Web fetch failed ({exc}), using fallback rankings.")
        return dict(FALLBACK_FIFA_RANKINGS)


def fetch_fifa_rankings() -> Dict[str, dict]:
    """
    Primary entry point. Returns FIFA-style ranking data for WC2026 teams.
    """
    return fetch_elo_ratings()


def load_teams_from_json(path: str | None = None) -> list[dict]:
    """Load team metadata from the bundled JSON file."""
    if path is None:
        path = os.path.join(
            os.path.dirname(__file__), "..", "data", "teams_2026.json"
        )
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data["teams"]
