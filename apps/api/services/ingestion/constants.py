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

# Maps football-data.org position strings → our Position enum
# Unmapped strings (e.g. "Goalkeeper" as a fallback) default to MID per design.
POSITION_MAP: dict[str, Position] = {
    "Goalkeeper": Position.GK,
    "Defender": Position.DEF,
    "Midfielder": Position.MID,
    "Forward": Position.FWD,
    "Attacker": Position.FWD,
    # Compact forms sometimes returned
    "GK": Position.GK,
    "DEF": Position.DEF,
    "MID": Position.MID,
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
