"""
Shared helpers for the ingestion layer.

These functions are pure transformations or simple DB look-ups reused
across multiple sync services.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from models.competition import Competition
from models.enums import FixtureStatus, Position
from models.season import Season
from services.ingestion.constants import (
    CURRENT_SEASON_END,
    CURRENT_SEASON_LABEL,
    CURRENT_SEASON_START,
    DEFAULT_PRICES,
    FIXTURE_STATUS_MAP,
    POSITION_MAP,
)


def normalize_position(raw: Optional[str]) -> Position:
    """Return the Position enum for a football-data.org position string.

    Falls back to MID for unknown/null values — keeps ingestion robust against
    API schema changes.
    """
    if raw is None:
        return Position.MID
    return POSITION_MAP.get(raw, Position.MID)


def normalize_fixture_status(raw: Optional[str]) -> FixtureStatus:
    """Return the FixtureStatus enum for a football-data.org match status string."""
    if raw is None:
        return FixtureStatus.SCHEDULED
    return FIXTURE_STATUS_MAP.get(raw, FixtureStatus.SCHEDULED)


def get_default_price(position: Position) -> float:
    """Return the starting price for a newly ingested player."""
    return DEFAULT_PRICES[position]


def get_or_create_season(db: Session) -> Season:
    """Return the current Season row, creating it if it doesn't exist yet."""
    season = db.query(Season).filter_by(label=CURRENT_SEASON_LABEL).first()
    if season is None:
        season = Season(
            label=CURRENT_SEASON_LABEL,
            start_date=datetime.fromisoformat(CURRENT_SEASON_START).replace(tzinfo=timezone.utc),
            end_date=datetime.fromisoformat(CURRENT_SEASON_END).replace(tzinfo=timezone.utc),
            is_active=True,
        )
        db.add(season)
        db.flush()
    return season


def get_competition_by_code(db: Session, code: str) -> Optional[Competition]:
    """Look up a competition by its football-data.org code."""
    return db.query(Competition).filter_by(code=code).first()
