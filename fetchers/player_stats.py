"""
fetchers/player_stats.py
Fetches player stats from FBref/Transfermarkt with hardcoded fallback.
"""
from __future__ import annotations
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT
from models.player import Player

# Top players per team — last 5 years stats (fallback hardcoded data)
FALLBACK_PLAYERS: Dict[str, List[dict]] = {
    "Argentina": [
        {"name": "Lionel Messi",        "position": "FWD", "age": 38, "goals_per_game": 0.82, "assists_per_game": 0.65, "games_played": 180, "trophies": 6, "market_value_m": 25.0,  "form_score": 78, "fitness": 0.85},
        {"name": "Julian Alvarez",       "position": "FWD", "age": 25, "goals_per_game": 0.55, "assists_per_game": 0.32, "games_played": 195, "trophies": 5, "market_value_m": 90.0,  "form_score": 88},
        {"name": "Rodrigo De Paul",      "position": "MID", "age": 31, "goals_per_game": 0.15, "assists_per_game": 0.25, "games_played": 180, "trophies": 4, "market_value_m": 35.0,  "form_score": 80},
        {"name": "Enzo Fernandez",       "position": "MID", "age": 24, "goals_per_game": 0.18, "assists_per_game": 0.22, "games_played": 170, "trophies": 3, "market_value_m": 100.0, "form_score": 82},
        {"name": "Emiliano Martinez",    "position": "GK",  "age": 32, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 200, "trophies": 5, "market_value_m": 35.0,  "form_score": 89},
    ],
    "France": [
        {"name": "Kylian Mbappe",        "position": "FWD", "age": 27, "goals_per_game": 0.78, "assists_per_game": 0.42, "games_played": 210, "trophies": 5, "market_value_m": 180.0, "form_score": 90},
        {"name": "Antoine Griezmann",    "position": "FWD", "age": 35, "goals_per_game": 0.45, "assists_per_game": 0.38, "games_played": 190, "trophies": 5, "market_value_m": 20.0,  "form_score": 75},
        {"name": "Aurelien Tchouameni", "position": "MID", "age": 26, "goals_per_game": 0.12, "assists_per_game": 0.15, "games_played": 175, "trophies": 3, "market_value_m": 80.0,  "form_score": 83},
        {"name": "William Saliba",       "position": "DEF", "age": 25, "goals_per_game": 0.05, "assists_per_game": 0.05, "games_played": 185, "trophies": 3, "market_value_m": 90.0,  "form_score": 88},
        {"name": "Mike Maignan",         "position": "GK",  "age": 30, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 195, "trophies": 4, "market_value_m": 45.0,  "form_score": 88},
    ],
    "Spain": [
        {"name": "Pedri",                "position": "MID", "age": 23, "goals_per_game": 0.20, "assists_per_game": 0.28, "games_played": 160, "trophies": 4, "market_value_m": 120.0, "form_score": 88},
        {"name": "Lamine Yamal",         "position": "FWD", "age": 18, "goals_per_game": 0.35, "assists_per_game": 0.45, "games_played": 130, "trophies": 3, "market_value_m": 180.0, "form_score": 92},
        {"name": "Alvaro Morata",        "position": "FWD", "age": 33, "goals_per_game": 0.42, "assists_per_game": 0.22, "games_played": 175, "trophies": 4, "market_value_m": 20.0,  "form_score": 78},
        {"name": "Rodri",                "position": "MID", "age": 29, "goals_per_game": 0.10, "assists_per_game": 0.18, "games_played": 190, "trophies": 6, "market_value_m": 100.0, "form_score": 85, "fitness": 0.80},
        {"name": "Unai Simon",           "position": "GK",  "age": 28, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 180, "trophies": 3, "market_value_m": 30.0,  "form_score": 82},
    ],
    "England": [
        {"name": "Jude Bellingham",      "position": "MID", "age": 22, "goals_per_game": 0.38, "assists_per_game": 0.32, "games_played": 185, "trophies": 4, "market_value_m": 180.0, "form_score": 90},
        {"name": "Harry Kane",           "position": "FWD", "age": 33, "goals_per_game": 0.72, "assists_per_game": 0.35, "games_played": 200, "trophies": 3, "market_value_m": 80.0,  "form_score": 87},
        {"name": "Phil Foden",           "position": "MID", "age": 26, "goals_per_game": 0.38, "assists_per_game": 0.35, "games_played": 190, "trophies": 5, "market_value_m": 140.0, "form_score": 88},
        {"name": "Bukayo Saka",          "position": "FWD", "age": 24, "goals_per_game": 0.32, "assists_per_game": 0.40, "games_played": 195, "trophies": 4, "market_value_m": 150.0, "form_score": 89},
        {"name": "Jordan Pickford",      "position": "GK",  "age": 32, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 185, "trophies": 2, "market_value_m": 25.0,  "form_score": 80},
    ],
    "Brazil": [
        {"name": "Vinicius Jr",          "position": "FWD", "age": 25, "goals_per_game": 0.55, "assists_per_game": 0.45, "games_played": 195, "trophies": 4, "market_value_m": 180.0, "form_score": 91},
        {"name": "Rodrygo",              "position": "FWD", "age": 24, "goals_per_game": 0.40, "assists_per_game": 0.38, "games_played": 185, "trophies": 4, "market_value_m": 120.0, "form_score": 87},
        {"name": "Raphinha",             "position": "FWD", "age": 28, "goals_per_game": 0.38, "assists_per_game": 0.42, "games_played": 190, "trophies": 4, "market_value_m": 90.0,  "form_score": 88},
        {"name": "Bruno Guimaraes",      "position": "MID", "age": 27, "goals_per_game": 0.18, "assists_per_game": 0.22, "games_played": 185, "trophies": 3, "market_value_m": 80.0,  "form_score": 85},
        {"name": "Alisson",              "position": "GK",  "age": 33, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 195, "trophies": 4, "market_value_m": 40.0,  "form_score": 86},
    ],
    "Portugal": [
        {"name": "Cristiano Ronaldo",    "position": "FWD", "age": 41, "goals_per_game": 0.62, "assists_per_game": 0.22, "games_played": 165, "trophies": 4, "market_value_m": 10.0,  "form_score": 70, "fitness": 0.75},
        {"name": "Bernardo Silva",       "position": "MID", "age": 31, "goals_per_game": 0.25, "assists_per_game": 0.35, "games_played": 195, "trophies": 5, "market_value_m": 80.0,  "form_score": 87},
        {"name": "Rafael Leao",          "position": "FWD", "age": 26, "goals_per_game": 0.42, "assists_per_game": 0.40, "games_played": 185, "trophies": 3, "market_value_m": 100.0, "form_score": 86},
        {"name": "Ruben Dias",           "position": "DEF", "age": 28, "goals_per_game": 0.05, "assists_per_game": 0.05, "games_played": 190, "trophies": 4, "market_value_m": 70.0,  "form_score": 87},
        {"name": "Diogo Costa",          "position": "GK",  "age": 26, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 175, "trophies": 2, "market_value_m": 40.0,  "form_score": 83},
    ],
    "Germany": [
        {"name": "Florian Wirtz",        "position": "MID", "age": 22, "goals_per_game": 0.35, "assists_per_game": 0.45, "games_played": 165, "trophies": 3, "market_value_m": 150.0, "form_score": 91},
        {"name": "Jamal Musiala",        "position": "MID", "age": 22, "goals_per_game": 0.32, "assists_per_game": 0.38, "games_played": 175, "trophies": 3, "market_value_m": 130.0, "form_score": 89},
        {"name": "Kai Havertz",          "position": "FWD", "age": 26, "goals_per_game": 0.38, "assists_per_game": 0.25, "games_played": 185, "trophies": 3, "market_value_m": 75.0,  "form_score": 83},
        {"name": "Joshua Kimmich",       "position": "MID", "age": 31, "goals_per_game": 0.12, "assists_per_game": 0.28, "games_played": 195, "trophies": 5, "market_value_m": 50.0,  "form_score": 85},
        {"name": "Manuel Neuer",         "position": "GK",  "age": 40, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 155, "trophies": 6, "market_value_m": 5.0,   "form_score": 72, "fitness": 0.80},
    ],
    "Netherlands": [
        {"name": "Virgil van Dijk",      "position": "DEF", "age": 35, "goals_per_game": 0.10, "assists_per_game": 0.08, "games_played": 185, "trophies": 3, "market_value_m": 25.0,  "form_score": 82},
        {"name": "Xavi Simons",          "position": "MID", "age": 23, "goals_per_game": 0.28, "assists_per_game": 0.38, "games_played": 170, "trophies": 2, "market_value_m": 100.0, "form_score": 87},
        {"name": "Tijjani Reijnders",    "position": "MID", "age": 27, "goals_per_game": 0.20, "assists_per_game": 0.25, "games_played": 175, "trophies": 3, "market_value_m": 60.0,  "form_score": 84},
        {"name": "Cody Gakpo",           "position": "FWD", "age": 26, "goals_per_game": 0.42, "assists_per_game": 0.35, "games_played": 180, "trophies": 3, "market_value_m": 65.0,  "form_score": 83},
        {"name": "Bart Verbruggen",      "position": "GK",  "age": 23, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 140, "trophies": 1, "market_value_m": 35.0,  "form_score": 80},
    ],
    "Morocco": [
        {"name": "Achraf Hakimi",        "position": "DEF", "age": 27, "goals_per_game": 0.18, "assists_per_game": 0.35, "games_played": 195, "trophies": 4, "market_value_m": 60.0,  "form_score": 87},
        {"name": "Hakim Ziyech",         "position": "MID", "age": 33, "goals_per_game": 0.28, "assists_per_game": 0.38, "games_played": 175, "trophies": 3, "market_value_m": 15.0,  "form_score": 76},
        {"name": "Youssef En-Nesyri",    "position": "FWD", "age": 29, "goals_per_game": 0.48, "assists_per_game": 0.18, "games_played": 180, "trophies": 2, "market_value_m": 30.0,  "form_score": 80},
        {"name": "Sofyan Amrabat",       "position": "MID", "age": 29, "goals_per_game": 0.08, "assists_per_game": 0.12, "games_played": 185, "trophies": 2, "market_value_m": 25.0,  "form_score": 82},
        {"name": "Yassine Bounou",       "position": "GK",  "age": 33, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 180, "trophies": 2, "market_value_m": 18.0,  "form_score": 83},
    ],
    "Belgium": [
        {"name": "Kevin De Bruyne",      "position": "MID", "age": 35, "goals_per_game": 0.20, "assists_per_game": 0.48, "games_played": 160, "trophies": 5, "market_value_m": 30.0,  "form_score": 78, "fitness": 0.82},
        {"name": "Romelu Lukaku",        "position": "FWD", "age": 33, "goals_per_game": 0.58, "assists_per_game": 0.22, "games_played": 175, "trophies": 2, "market_value_m": 15.0,  "form_score": 72},
        {"name": "Lois Openda",          "position": "FWD", "age": 25, "goals_per_game": 0.55, "assists_per_game": 0.28, "games_played": 170, "trophies": 2, "market_value_m": 60.0,  "form_score": 84},
        {"name": "Youri Tielemans",      "position": "MID", "age": 29, "goals_per_game": 0.15, "assists_per_game": 0.22, "games_played": 185, "trophies": 2, "market_value_m": 35.0,  "form_score": 78},
        {"name": "Koen Casteels",        "position": "GK",  "age": 33, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 175, "trophies": 1, "market_value_m": 15.0,  "form_score": 79},
    ],
    "Japan": [
        {"name": "Takefusa Kubo",        "position": "FWD", "age": 23, "goals_per_game": 0.32, "assists_per_game": 0.38, "games_played": 175, "trophies": 2, "market_value_m": 60.0,  "form_score": 85},
        {"name": "Kaoru Mitoma",         "position": "FWD", "age": 28, "goals_per_game": 0.38, "assists_per_game": 0.42, "games_played": 180, "trophies": 2, "market_value_m": 55.0,  "form_score": 84},
        {"name": "Wataru Endo",          "position": "MID", "age": 32, "goals_per_game": 0.10, "assists_per_game": 0.15, "games_played": 190, "trophies": 2, "market_value_m": 25.0,  "form_score": 80},
        {"name": "Ritsu Doan",           "position": "MID", "age": 27, "goals_per_game": 0.28, "assists_per_game": 0.30, "games_played": 180, "trophies": 2, "market_value_m": 30.0,  "form_score": 82},
        {"name": "Zion Suzuki",          "position": "GK",  "age": 23, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 140, "trophies": 1, "market_value_m": 15.0,  "form_score": 78},
    ],
    "Croatia": [
        {"name": "Luka Modric",          "position": "MID", "age": 41, "goals_per_game": 0.12, "assists_per_game": 0.25, "games_played": 155, "trophies": 5, "market_value_m": 8.0,   "form_score": 70, "fitness": 0.78},
        {"name": "Ivan Perisic",         "position": "MID", "age": 37, "goals_per_game": 0.22, "assists_per_game": 0.28, "games_played": 150, "trophies": 2, "market_value_m": 5.0,   "form_score": 68},
        {"name": "Mateo Kovacic",        "position": "MID", "age": 32, "goals_per_game": 0.12, "assists_per_game": 0.22, "games_played": 180, "trophies": 5, "market_value_m": 35.0,  "form_score": 82},
        {"name": "Andrej Kramaric",      "position": "FWD", "age": 34, "goals_per_game": 0.45, "assists_per_game": 0.28, "games_played": 175, "trophies": 2, "market_value_m": 12.0,  "form_score": 76},
        {"name": "Dominik Livakovic",    "position": "GK",  "age": 30, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 180, "trophies": 1, "market_value_m": 20.0,  "form_score": 82},
    ],
    "Uruguay": [
        {"name": "Darwin Nunez",         "position": "FWD", "age": 26, "goals_per_game": 0.52, "assists_per_game": 0.32, "games_played": 180, "trophies": 2, "market_value_m": 80.0,  "form_score": 82},
        {"name": "Federico Valverde",    "position": "MID", "age": 26, "goals_per_game": 0.22, "assists_per_game": 0.28, "games_played": 185, "trophies": 4, "market_value_m": 100.0, "form_score": 88},
        {"name": "Ronald Araujo",        "position": "DEF", "age": 26, "goals_per_game": 0.08, "assists_per_game": 0.05, "games_played": 165, "trophies": 3, "market_value_m": 50.0,  "form_score": 82},
        {"name": "Rodrigo Bentancur",    "position": "MID", "age": 28, "goals_per_game": 0.10, "assists_per_game": 0.18, "games_played": 175, "trophies": 3, "market_value_m": 45.0,  "form_score": 80},
        {"name": "Sergio Rochet",        "position": "GK",  "age": 29, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 170, "trophies": 1, "market_value_m": 12.0,  "form_score": 78},
    ],
    "Colombia": [
        {"name": "James Rodriguez",      "position": "MID", "age": 34, "goals_per_game": 0.22, "assists_per_game": 0.40, "games_played": 155, "trophies": 1, "market_value_m": 10.0,  "form_score": 72},
        {"name": "Luis Diaz",            "position": "FWD", "age": 28, "goals_per_game": 0.42, "assists_per_game": 0.38, "games_played": 185, "trophies": 2, "market_value_m": 70.0,  "form_score": 85},
        {"name": "Richard Rios",         "position": "MID", "age": 25, "goals_per_game": 0.18, "assists_per_game": 0.22, "games_played": 155, "trophies": 1, "market_value_m": 35.0,  "form_score": 80},
        {"name": "Jhon Duran",           "position": "FWD", "age": 21, "goals_per_game": 0.48, "assists_per_game": 0.22, "games_played": 130, "trophies": 1, "market_value_m": 60.0,  "form_score": 83},
        {"name": "David Ospina",         "position": "GK",  "age": 38, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 150, "trophies": 1, "market_value_m": 3.0,   "form_score": 68, "fitness": 0.80},
    ],
    "USA": [
        {"name": "Christian Pulisic",    "position": "FWD", "age": 27, "goals_per_game": 0.35, "assists_per_game": 0.35, "games_played": 185, "trophies": 2, "market_value_m": 35.0,  "form_score": 83},
        {"name": "Weston McKennie",      "position": "MID", "age": 27, "goals_per_game": 0.18, "assists_per_game": 0.20, "games_played": 170, "trophies": 2, "market_value_m": 28.0,  "form_score": 78},
        {"name": "Tyler Adams",          "position": "MID", "age": 27, "goals_per_game": 0.08, "assists_per_game": 0.12, "games_played": 155, "trophies": 1, "market_value_m": 30.0,  "form_score": 75, "fitness": 0.82},
        {"name": "Folarin Balogun",      "position": "FWD", "age": 24, "goals_per_game": 0.45, "assists_per_game": 0.22, "games_played": 155, "trophies": 1, "market_value_m": 35.0,  "form_score": 80},
        {"name": "Matt Turner",          "position": "GK",  "age": 31, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 165, "trophies": 1, "market_value_m": 8.0,   "form_score": 76},
    ],
    "Mexico": [
        {"name": "Santiago Gimenez",     "position": "FWD", "age": 24, "goals_per_game": 0.52, "assists_per_game": 0.25, "games_played": 170, "trophies": 2, "market_value_m": 50.0,  "form_score": 84},
        {"name": "Hirving Lozano",       "position": "FWD", "age": 30, "goals_per_game": 0.35, "assists_per_game": 0.35, "games_played": 175, "trophies": 3, "market_value_m": 20.0,  "form_score": 76},
        {"name": "Edson Alvarez",        "position": "MID", "age": 27, "goals_per_game": 0.10, "assists_per_game": 0.15, "games_played": 180, "trophies": 2, "market_value_m": 35.0,  "form_score": 80},
        {"name": "Jorge Sanchez",        "position": "DEF", "age": 25, "goals_per_game": 0.05, "assists_per_game": 0.12, "games_played": 165, "trophies": 2, "market_value_m": 15.0,  "form_score": 75},
        {"name": "Guillermo Ochoa",      "position": "GK",  "age": 40, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 160, "trophies": 3, "market_value_m": 2.0,   "form_score": 70, "fitness": 0.78},
    ],
    "Canada": [
        {"name": "Alphonso Davies",      "position": "DEF", "age": 25, "goals_per_game": 0.15, "assists_per_game": 0.35, "games_played": 185, "trophies": 3, "market_value_m": 70.0,  "form_score": 86},
        {"name": "Jonathan David",       "position": "FWD", "age": 25, "goals_per_game": 0.60, "assists_per_game": 0.28, "games_played": 185, "trophies": 2, "market_value_m": 65.0,  "form_score": 87},
        {"name": "Tajon Buchanan",       "position": "MID", "age": 26, "goals_per_game": 0.22, "assists_per_game": 0.30, "games_played": 165, "trophies": 1, "market_value_m": 20.0,  "form_score": 78},
        {"name": "Liam Millar",          "position": "FWD", "age": 26, "goals_per_game": 0.25, "assists_per_game": 0.22, "games_played": 155, "trophies": 1, "market_value_m": 10.0,  "form_score": 74},
        {"name": "Maxime Crepeau",       "position": "GK",  "age": 30, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 165, "trophies": 1, "market_value_m": 5.0,   "form_score": 74},
    ],
    "Ecuador": [
        {"name": "Enner Valencia",       "position": "FWD", "age": 36, "goals_per_game": 0.50, "assists_per_game": 0.22, "games_played": 165, "trophies": 1, "market_value_m": 4.0,   "form_score": 70, "fitness": 0.78},
        {"name": "Moisés Caicedo",       "position": "MID", "age": 24, "goals_per_game": 0.12, "assists_per_game": 0.18, "games_played": 175, "trophies": 1, "market_value_m": 100.0, "form_score": 84},
        {"name": "Jeremy Sarmiento",     "position": "MID", "age": 23, "goals_per_game": 0.18, "assists_per_game": 0.25, "games_played": 150, "trophies": 1, "market_value_m": 18.0,  "form_score": 76},
        {"name": "Djorkaeff Reasco",     "position": "FWD", "age": 24, "goals_per_game": 0.28, "assists_per_game": 0.22, "games_played": 140, "trophies": 1, "market_value_m": 12.0,  "form_score": 74},
        {"name": "Hernan Galindez",      "position": "GK",  "age": 37, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 155, "trophies": 0, "market_value_m": 2.0,   "form_score": 68},
    ],
    "Switzerland": [
        {"name": "Granit Xhaka",         "position": "MID", "age": 33, "goals_per_game": 0.12, "assists_per_game": 0.20, "games_played": 185, "trophies": 3, "market_value_m": 20.0,  "form_score": 80},
        {"name": "Xherdan Shaqiri",      "position": "MID", "age": 34, "goals_per_game": 0.22, "assists_per_game": 0.28, "games_played": 165, "trophies": 1, "market_value_m": 5.0,   "form_score": 72},
        {"name": "Ruben Vargas",         "position": "FWD", "age": 26, "goals_per_game": 0.28, "assists_per_game": 0.30, "games_played": 175, "trophies": 1, "market_value_m": 20.0,  "form_score": 79},
        {"name": "Manuel Akanji",        "position": "DEF", "age": 30, "goals_per_game": 0.05, "assists_per_game": 0.08, "games_played": 185, "trophies": 3, "market_value_m": 40.0,  "form_score": 82},
        {"name": "Yann Sommer",          "position": "GK",  "age": 37, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 180, "trophies": 3, "market_value_m": 10.0,  "form_score": 79},
    ],
    "Senegal": [
        {"name": "Sadio Mane",           "position": "FWD", "age": 34, "goals_per_game": 0.50, "assists_per_game": 0.32, "games_played": 175, "trophies": 3, "market_value_m": 10.0,  "form_score": 73},
        {"name": "Edouard Mendy",        "position": "GK",  "age": 33, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 170, "trophies": 2, "market_value_m": 12.0,  "form_score": 76},
        {"name": "Ismaila Sarr",         "position": "FWD", "age": 27, "goals_per_game": 0.35, "assists_per_game": 0.30, "games_played": 175, "trophies": 1, "market_value_m": 28.0,  "form_score": 78},
        {"name": "Cheikhou Kouyate",     "position": "MID", "age": 35, "goals_per_game": 0.08, "assists_per_game": 0.10, "games_played": 165, "trophies": 2, "market_value_m": 3.0,   "form_score": 68},
        {"name": "Pape Matar Sarr",      "position": "MID", "age": 23, "goals_per_game": 0.12, "assists_per_game": 0.18, "games_played": 155, "trophies": 1, "market_value_m": 30.0,  "form_score": 78},
    ],
    "Italy": [
        {"name": "Federico Chiesa",      "position": "FWD", "age": 27, "goals_per_game": 0.32, "assists_per_game": 0.28, "games_played": 155, "trophies": 2, "market_value_m": 35.0,  "form_score": 74, "fitness": 0.80},
        {"name": "Sandro Tonali",        "position": "MID", "age": 25, "goals_per_game": 0.15, "assists_per_game": 0.20, "games_played": 165, "trophies": 2, "market_value_m": 55.0,  "form_score": 78},
        {"name": "Gianluca Scamacca",    "position": "FWD", "age": 26, "goals_per_game": 0.40, "assists_per_game": 0.20, "games_played": 155, "trophies": 2, "market_value_m": 40.0,  "form_score": 76},
        {"name": "Nicolo Barella",       "position": "MID", "age": 28, "goals_per_game": 0.15, "assists_per_game": 0.28, "games_played": 185, "trophies": 4, "market_value_m": 65.0,  "form_score": 84},
        {"name": "Gianluigi Donnarumma", "position": "GK",  "age": 27, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 185, "trophies": 3, "market_value_m": 50.0,  "form_score": 84},
    ],
    "Denmark": [
        {"name": "Christian Eriksen",    "position": "MID", "age": 34, "goals_per_game": 0.18, "assists_per_game": 0.35, "games_played": 165, "trophies": 2, "market_value_m": 10.0,  "form_score": 76},
        {"name": "Rasmus Hojlund",       "position": "FWD", "age": 23, "goals_per_game": 0.48, "assists_per_game": 0.22, "games_played": 160, "trophies": 1, "market_value_m": 60.0,  "form_score": 79},
        {"name": "Andreas Christensen",  "position": "DEF", "age": 29, "goals_per_game": 0.05, "assists_per_game": 0.05, "games_played": 170, "trophies": 3, "market_value_m": 30.0,  "form_score": 78},
        {"name": "Pierre-Emile Hojbjerg","position": "MID", "age": 30, "goals_per_game": 0.10, "assists_per_game": 0.15, "games_played": 185, "trophies": 1, "market_value_m": 30.0,  "form_score": 76},
        {"name": "Kasper Schmeichel",    "position": "GK",  "age": 39, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 160, "trophies": 2, "market_value_m": 4.0,   "form_score": 74},
    ],
    "Poland": [
        {"name": "Robert Lewandowski",   "position": "FWD", "age": 38, "goals_per_game": 0.70, "assists_per_game": 0.28, "games_played": 185, "trophies": 5, "market_value_m": 15.0,  "form_score": 80, "fitness": 0.83},
        {"name": "Piotr Zielinski",      "position": "MID", "age": 32, "goals_per_game": 0.18, "assists_per_game": 0.28, "games_played": 180, "trophies": 3, "market_value_m": 30.0,  "form_score": 78},
        {"name": "Wojciech Szczesny",    "position": "GK",  "age": 36, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 170, "trophies": 3, "market_value_m": 5.0,   "form_score": 76},
        {"name": "Jan Bednarek",         "position": "DEF", "age": 29, "goals_per_game": 0.05, "assists_per_game": 0.05, "games_played": 175, "trophies": 1, "market_value_m": 20.0,  "form_score": 74},
        {"name": "Bartosz Slisz",        "position": "MID", "age": 26, "goals_per_game": 0.10, "assists_per_game": 0.15, "games_played": 155, "trophies": 1, "market_value_m": 12.0,  "form_score": 72},
    ],
    "South Korea": [
        {"name": "Son Heung-min",        "position": "FWD", "age": 34, "goals_per_game": 0.52, "assists_per_game": 0.38, "games_played": 190, "trophies": 2, "market_value_m": 20.0,  "form_score": 80},
        {"name": "Lee Kang-in",          "position": "MID", "age": 24, "goals_per_game": 0.28, "assists_per_game": 0.38, "games_played": 175, "trophies": 2, "market_value_m": 40.0,  "form_score": 83},
        {"name": "Kim Min-jae",          "position": "DEF", "age": 28, "goals_per_game": 0.08, "assists_per_game": 0.05, "games_played": 180, "trophies": 3, "market_value_m": 50.0,  "form_score": 83},
        {"name": "Hwang Hee-chan",        "position": "FWD", "age": 29, "goals_per_game": 0.38, "assists_per_game": 0.25, "games_played": 175, "trophies": 1, "market_value_m": 22.0,  "form_score": 78},
        {"name": "Cho Hyun-woo",         "position": "GK",  "age": 34, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 165, "trophies": 1, "market_value_m": 5.0,   "form_score": 74},
    ],
    "Iran": [
        {"name": "Mehdi Taremi",         "position": "FWD", "age": 32, "goals_per_game": 0.55, "assists_per_game": 0.28, "games_played": 185, "trophies": 2, "market_value_m": 15.0,  "form_score": 78},
        {"name": "Sardar Azmoun",        "position": "FWD", "age": 30, "goals_per_game": 0.48, "assists_per_game": 0.30, "games_played": 170, "trophies": 1, "market_value_m": 12.0,  "form_score": 74},
        {"name": "Alireza Jahanbakhsh",  "position": "MID", "age": 31, "goals_per_game": 0.22, "assists_per_game": 0.28, "games_played": 165, "trophies": 1, "market_value_m": 8.0,   "form_score": 72},
        {"name": "Ali Gholizadeh",       "position": "MID", "age": 27, "goals_per_game": 0.18, "assists_per_game": 0.22, "games_played": 155, "trophies": 1, "market_value_m": 5.0,   "form_score": 70},
        {"name": "Alireza Beiranvand",   "position": "GK",  "age": 33, "goals_per_game": 0.0,  "assists_per_game": 0.0,  "games_played": 165, "trophies": 1, "market_value_m": 4.0,   "form_score": 70},
    ],
}

# For teams not in the detailed fallback, generate generic players
def _generic_players(team_name: str, quality: float) -> List[dict]:
    positions = ["GK", "DEF", "DEF", "MID", "FWD"]
    players = []
    for i, pos in enumerate(positions):
        gpg = (quality / 100) * 0.5 if pos == "FWD" else (quality / 100) * 0.15 if pos == "MID" else 0.0
        players.append({
            "name": f"{team_name} Player {i+1}",
            "position": pos,
            "age": 26,
            "goals_per_game": gpg,
            "assists_per_game": gpg * 0.6,
            "games_played": 150,
            "trophies": max(0, int(quality / 30)),
            "market_value_m": quality * 0.5,
            "form_score": quality,
        })
    return players


def fetch_player_stats(team_name: str, quality_fallback: float = 60.0) -> List[Player]:
    """
    Fetch key players for a team. Uses hardcoded data, no live scraping needed.
    """
    raw_players = FALLBACK_PLAYERS.get(team_name, _generic_players(team_name, quality_fallback))
    players = []
    for p in raw_players:
        player = Player(
            name=p["name"],
            team=team_name,
            position=p["position"],
            age=p.get("age", 25),
            goals_per_game=p.get("goals_per_game", 0.0),
            assists_per_game=p.get("assists_per_game", 0.0),
            games_played=p.get("games_played", 150),
            trophies=p.get("trophies", 0),
            market_value_m=p.get("market_value_m", 10.0),
            fitness=p.get("fitness", 1.0),
            is_injured=p.get("is_injured", False),
            form_score=p.get("form_score", 65.0),
        )
        players.append(player)
    return players
