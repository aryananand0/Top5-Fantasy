"""
Static configuration for the ingestion layer.

All football-data.org competition codes, position mappings, and fixture-status
mappings live here so sync services don't hard-code magic strings.
"""

from models.enums import FixtureStatus, Position

# football-data.org competition codes for the Top 5 leagues
SUPPORTED_COMPETITIONS: list[dict] = [
    {"code": "PL",  "name": "Premier League",   "country": "England"},
    {"code": "PD",  "name": "La Liga",           "country": "Spain"},
    {"code": "BL1", "name": "Bundesliga",         "country": "Germany"},
    {"code": "SA",  "name": "Serie A",            "country": "Italy"},
    {"code": "FL1", "name": "Ligue 1",            "country": "France"},
]

# Maps football-data.org position strings → our Position enum.
# The API returns granular sub-positions (e.g. "Centre-Back", "Left Winger")
# rather than the four broad values, so we map every known variant.
# Unknown strings fall back to MID in normalize_position().
POSITION_MAP: dict[str, Position] = {
    # Goalkeepers
    "Goalkeeper": Position.GK,
    "GK": Position.GK,

    # Defenders — all back-line sub-positions
    "Defender": Position.DEF,
    "Centre-Back": Position.DEF,
    "Left-Back": Position.DEF,
    "Right-Back": Position.DEF,
    "Left Back": Position.DEF,
    "Right Back": Position.DEF,
    "Wing-Back": Position.DEF,
    "Sweeper": Position.DEF,
    "Defence": Position.DEF,
    "DEF": Position.DEF,

    # Midfielders — all central and wide mid sub-positions
    "Midfielder": Position.MID,
    "Central Midfield": Position.MID,
    "Defensive Midfield": Position.MID,
    "Attacking Midfield": Position.MID,
    "Left Midfield": Position.MID,
    "Right Midfield": Position.MID,
    "Midfield": Position.MID,
    "MID": Position.MID,

    # Forwards — all attacking sub-positions
    "Forward": Position.FWD,
    "Attacker": Position.FWD,
    "Centre-Forward": Position.FWD,
    "Left Winger": Position.FWD,
    "Right Winger": Position.FWD,
    "Second Striker": Position.FWD,
    "Offence": Position.FWD,
    "FWD": Position.FWD,
}

# Maps football-data.org match status strings → our FixtureStatus enum
FIXTURE_STATUS_MAP: dict[str, FixtureStatus] = {
    "SCHEDULED": FixtureStatus.SCHEDULED,
    "TIMED": FixtureStatus.SCHEDULED,
    "IN_PLAY": FixtureStatus.LIVE,
    "PAUSED": FixtureStatus.LIVE,
    "FINISHED": FixtureStatus.FINISHED,
    "AWARDED": FixtureStatus.FINISHED,
    "POSTPONED": FixtureStatus.POSTPONED,
    "SUSPENDED": FixtureStatus.POSTPONED,
    "CANCELLED": FixtureStatus.CANCELLED,
}

# Default starting prices by position (in £m units stored as Decimal)
DEFAULT_PRICES: dict[Position, float] = {
    Position.GK:  4.5,
    Position.DEF: 4.5,
    Position.MID: 5.0,
    Position.FWD: 5.5,
}

# Current active season label — change each year
CURRENT_SEASON_LABEL = "2024-25"
CURRENT_SEASON_START = "2024-08-01"
CURRENT_SEASON_END = "2025-06-01"
