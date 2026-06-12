"""
Configuration and constants for the World Cup 2026 Simulator.
"""

# ─── Simulation Parameters ────────────────────────────────────────────────────
NUM_SIMULATIONS: int = 10_000
QUICK_SIMULATIONS: int = 100

# ─── Model Weights ────────────────────────────────────────────────────────────
WEIGHT_FIFA_RANKING: float = 0.25
WEIGHT_RECENT_FORM: float = 0.30
WEIGHT_PLAYER_QUALITY: float = 0.25
WEIGHT_H2H: float = 0.10
WEIGHT_CONTEXT: float = 0.10  # weather, altitude, host, political

# ─── API Endpoints ────────────────────────────────────────────────────────────
FIFA_RANKING_URL = "https://www.fifa.com/fifa-world-ranking/men"
ELO_RATINGS_URL = "https://www.eloratings.net/"
ESPN_SOCCER_URL = "https://www.espn.com/soccer/"
BBC_FOOTBALL_URL = "https://www.bbc.com/sport/football"
MARCA_URL = "https://www.marca.com"
FBREF_URL = "https://fbref.com/en/comps/Big5/"
TRANSFERMARKT_URL = "https://www.transfermarkt.com/statistik/weltrangliste"
H2H_URL = "https://www.11v11.com/"
SOCCERWAY_URL = "https://www.soccerway.com"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# ─── Request Settings ─────────────────────────────────────────────────────────
REQUEST_TIMEOUT: int = 10
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ─── WC2026 Venues ────────────────────────────────────────────────────────────
VENUES = {
    # USA
    "Miami": {"country": "USA", "city": "Miami", "temp_c": 35, "humidity": 80, "altitude_m": 0},
    "Dallas": {"country": "USA", "city": "Dallas", "temp_c": 38, "humidity": 30, "altitude_m": 130},
    "New York": {"country": "USA", "city": "New York", "temp_c": 28, "humidity": 55, "altitude_m": 0},
    "Los Angeles": {"country": "USA", "city": "Los Angeles", "temp_c": 30, "humidity": 35, "altitude_m": 71},
    "Seattle": {"country": "USA", "city": "Seattle", "temp_c": 22, "humidity": 65, "altitude_m": 0},
    "San Francisco": {"country": "USA", "city": "San Francisco", "temp_c": 20, "humidity": 70, "altitude_m": 0},
    "Boston": {"country": "USA", "city": "Boston", "temp_c": 27, "humidity": 60, "altitude_m": 0},
    "Kansas City": {"country": "USA", "city": "Kansas City", "temp_c": 33, "humidity": 50, "altitude_m": 270},
    "Houston": {"country": "USA", "city": "Houston", "temp_c": 36, "humidity": 80, "altitude_m": 0},
    "Atlanta": {"country": "USA", "city": "Atlanta", "temp_c": 34, "humidity": 75, "altitude_m": 320},
    "Philadelphia": {"country": "USA", "city": "Philadelphia", "temp_c": 29, "humidity": 60, "altitude_m": 0},
    # Mexico
    "Guadalajara": {"country": "Mexico", "city": "Guadalajara", "temp_c": 28, "humidity": 45, "altitude_m": 1566},
    "Mexico City": {"country": "Mexico", "city": "Mexico City", "temp_c": 22, "humidity": 40, "altitude_m": 2240},
    "Monterrey": {"country": "Mexico", "city": "Monterrey", "temp_c": 38, "humidity": 35, "altitude_m": 540},
    # Canada
    "Toronto": {"country": "Canada", "city": "Toronto", "temp_c": 26, "humidity": 65, "altitude_m": 76},
    "Vancouver": {"country": "Canada", "city": "Vancouver", "temp_c": 23, "humidity": 70, "altitude_m": 0},
}

# ─── Host Teams ───────────────────────────────────────────────────────────────
HOST_TEAMS = {"USA", "Mexico", "Canada"}
HOST_ADVANTAGE_BOOST = 1.05  # 5% boost

# ─── Altitude Threshold ───────────────────────────────────────────────────────
ALTITUDE_THRESHOLD_M = 1500  # metres above which altitude matters
ALTITUDE_PENALTY_NON_ADAPTED = 0.05  # 5% penalty for non-adapted teams
# Teams considered adapted to altitude (play regularly >1500m)
ALTITUDE_ADAPTED_TEAMS = {"Bolivia", "Colombia", "Ecuador", "Mexico", "Peru"}

# ─── Simulation / Dixon-Coles model defaults ──────────────────────────────────
BASE_LAMBDA = 1.35           # average goals per team per match in WC
LAMBDA_MIN = 0.2             # floor for Poisson lambda
LAMBDA_MAX = 4.5             # ceiling

# Penalties (for draws in knockout rounds)
PENALTY_HOME_WIN_PROB = 0.47
PENALTY_AWAY_WIN_PROB = 0.47
PENALTY_DRAW_PROB = 0.06     # (extremely rarely both miss all 5 and still draw)

# ─── Known Political / Psychological Conflicts ────────────────────────────────
POLITICAL_CONFLICTS: dict[str, dict] = {
    frozenset({"USA", "Iran"}): {"tension": 0.9, "description": "High geopolitical tension"},
    frozenset({"USA", "Mexico"}): {"tension": 0.4, "description": "Historic rivalry, border tensions"},
    frozenset({"Argentina", "England"}): {"tension": 0.7, "description": "Malvinas/Falklands historical conflict"},
    frozenset({"Serbia", "Albania"}): {"tension": 0.85, "description": "Kosovo political tension"},
    frozenset({"Serbia", "Croatia"}): {"tension": 0.75, "description": "Balkan historical conflicts"},
    frozenset({"Serbia", "Slovenia"}): {"tension": 0.5, "description": "Historical tensions"},
    frozenset({"Morocco", "Algeria"}): {"tension": 0.6, "description": "North African regional rivalry"},
    frozenset({"South Korea", "Japan"}): {"tension": 0.55, "description": "Historical tensions"},
    frozenset({"Iran", "Saudi Arabia"}): {"tension": 0.8, "description": "Regional Middle East tension"},
    frozenset({"Nigeria", "Cameroon"}): {"tension": 0.3, "description": "West African rivalry"},
    frozenset({"Ghana", "Nigeria"}): {"tension": 0.35, "description": "West African rivalry"},
}

# ─── FIFA Rankings Fallback Data (Jan 2026) ───────────────────────────────────
FALLBACK_FIFA_RANKINGS: dict[str, dict] = {
    "Argentina":      {"points": 1900.0, "rank": 1,  "confederation": "CONMEBOL"},
    "France":         {"points": 1850.0, "rank": 2,  "confederation": "UEFA"},
    "Spain":          {"points": 1820.0, "rank": 3,  "confederation": "UEFA"},
    "England":        {"points": 1780.0, "rank": 4,  "confederation": "UEFA"},
    "Brazil":         {"points": 1760.0, "rank": 5,  "confederation": "CONMEBOL"},
    "Portugal":       {"points": 1740.0, "rank": 6,  "confederation": "UEFA"},
    "Netherlands":    {"points": 1720.0, "rank": 7,  "confederation": "UEFA"},
    "Germany":        {"points": 1700.0, "rank": 8,  "confederation": "UEFA"},
    "Morocco":        {"points": 1680.0, "rank": 9,  "confederation": "CAF"},
    "Belgium":        {"points": 1660.0, "rank": 10, "confederation": "UEFA"},
    "Japan":          {"points": 1640.0, "rank": 11, "confederation": "AFC"},
    "Croatia":        {"points": 1620.0, "rank": 12, "confederation": "UEFA"},
    "USA":            {"points": 1600.0, "rank": 13, "confederation": "CONCACAF"},
    "Colombia":       {"points": 1580.0, "rank": 14, "confederation": "CONMEBOL"},
    "Mexico":         {"points": 1560.0, "rank": 15, "confederation": "CONCACAF"},
    "Uruguay":        {"points": 1540.0, "rank": 16, "confederation": "CONMEBOL"},
    "Switzerland":    {"points": 1520.0, "rank": 17, "confederation": "UEFA"},
    "Senegal":        {"points": 1500.0, "rank": 18, "confederation": "CAF"},
    "Italy":          {"points": 1480.0, "rank": 19, "confederation": "UEFA"},
    "Denmark":        {"points": 1460.0, "rank": 20, "confederation": "UEFA"},
    "Ecuador":        {"points": 1440.0, "rank": 21, "confederation": "CONMEBOL"},
    "South Korea":    {"points": 1420.0, "rank": 22, "confederation": "AFC"},
    "Australia":      {"points": 1400.0, "rank": 23, "confederation": "AFC"},
    "Canada":         {"points": 1390.0, "rank": 24, "confederation": "CONCACAF"},
    "Austria":        {"points": 1380.0, "rank": 25, "confederation": "UEFA"},
    "Turkey":         {"points": 1360.0, "rank": 26, "confederation": "UEFA"},
    "Poland":         {"points": 1340.0, "rank": 27, "confederation": "UEFA"},
    "Ukraine":        {"points": 1320.0, "rank": 28, "confederation": "UEFA"},
    "Nigeria":        {"points": 1300.0, "rank": 29, "confederation": "CAF"},
    "Serbia":         {"points": 1280.0, "rank": 30, "confederation": "UEFA"},
    "Iran":           {"points": 1260.0, "rank": 31, "confederation": "AFC"},
    "Chile":          {"points": 1240.0, "rank": 32, "confederation": "CONMEBOL"},
    "Saudi Arabia":   {"points": 1220.0, "rank": 33, "confederation": "AFC"},
    "Romania":        {"points": 1200.0, "rank": 34, "confederation": "UEFA"},
    "Hungary":        {"points": 1180.0, "rank": 35, "confederation": "UEFA"},
    "Czech Republic": {"points": 1160.0, "rank": 36, "confederation": "UEFA"},
    "Albania":        {"points": 1140.0, "rank": 37, "confederation": "UEFA"},
    "Slovakia":       {"points": 1120.0, "rank": 38, "confederation": "UEFA"},
    "Scotland":       {"points": 1100.0, "rank": 39, "confederation": "UEFA"},
    "Venezuela":      {"points": 1080.0, "rank": 40, "confederation": "CONMEBOL"},
    "Paraguay":       {"points": 1060.0, "rank": 41, "confederation": "CONMEBOL"},
    "Bolivia":        {"points": 1040.0, "rank": 42, "confederation": "CONMEBOL"},
    "South Africa":   {"points": 1020.0, "rank": 43, "confederation": "CAF"},
    "Egypt":          {"points": 1000.0, "rank": 44, "confederation": "CAF"},
    "Cameroon":       {"points":  980.0, "rank": 45, "confederation": "CAF"},
    "DR Congo":       {"points":  960.0, "rank": 46, "confederation": "CAF"},
    "Panama":         {"points":  940.0, "rank": 47, "confederation": "CONCACAF"},
    "Honduras":       {"points":  920.0, "rank": 48, "confederation": "CONCACAF"},
    "Costa Rica":     {"points":  900.0, "rank": 49, "confederation": "CONCACAF"},
    "Jamaica":        {"points":  880.0, "rank": 50, "confederation": "CONCACAF"},
    "Slovenia":       {"points":  860.0, "rank": 51, "confederation": "UEFA"},
    "Georgia":        {"points":  840.0, "rank": 52, "confederation": "UEFA"},
    "Jordan":         {"points":  820.0, "rank": 53, "confederation": "AFC"},
    "Qatar":          {"points":  800.0, "rank": 54, "confederation": "AFC"},
    "Uzbekistan":     {"points":  780.0, "rank": 55, "confederation": "AFC"},
    "New Zealand":    {"points":  760.0, "rank": 56, "confederation": "OFC"},
    "Kenya":          {"points":  740.0, "rank": 57, "confederation": "CAF"},
    "Ghana":          {"points":  720.0, "rank": 58, "confederation": "CAF"},
    "Peru":           {"points":  700.0, "rank": 59, "confederation": "CONMEBOL"},
}
