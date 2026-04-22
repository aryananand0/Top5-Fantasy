"""
Top5 Fantasy — SQLAlchemy ORM models.

Import order matters for Alembic autogenerate to detect all tables.
All models must be imported here so Base.metadata is populated.
"""

from .base import Base, TimestampMixin
from .enums import DataQuality, FixtureStatus, GameweekStatus, Position, ScoringMode
from .user import User
from .season import Season
from .competition import Competition
from .team import Team
from .player import Player, PriceHistory
from .gameweek import Gameweek
from .fixture import Fixture, PlayerMatchStats
from .squad import Squad, SquadPlayer
from .lineup import GameweekLineup, GameweekLineupPlayer
from .transfer import Transfer
from .league import MiniLeague, LeagueMember
from .scoring import UserGameweekScore

__all__ = [
    "Base",
    "TimestampMixin",
    # Enums
    "DataQuality",
    "FixtureStatus",
    "GameweekStatus",
    "Position",
    "ScoringMode",
    # Models
    "User",
    "Season",
    "Competition",
    "Team",
    "Player",
    "PriceHistory",
    "Gameweek",
    "Fixture",
    "PlayerMatchStats",
    "Squad",
    "SquadPlayer",
    "GameweekLineup",
    "GameweekLineupPlayer",
    "Transfer",
    "MiniLeague",
    "LeagueMember",
    "UserGameweekScore",
]
