from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum as SAEnum, ForeignKey, Index,
    Integer, SmallInteger, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .enums import DataQuality, FixtureStatus, Position


class Fixture(Base):
    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competition_id: Mapped[int] = mapped_column(Integer, ForeignKey("competitions.id"), nullable=False)

    # Nullable: fixtures are ingested before gameweeks are always assigned.
    # A background job assigns gameweek_id when the GW window is defined.
    gameweek_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("gameweeks.id"), nullable=True
    )

    home_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=False)

    kickoff_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[FixtureStatus] = mapped_column(
        SAEnum(FixtureStatus, name="fixture_status_enum"),
        default=FixtureStatus.SCHEDULED,
        nullable=False,
    )

    home_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)

    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # football-data.org match ID

    # Tracks completeness of data received for this fixture.
    # Scoring job uses this to decide whether to apply RICH or FALLBACK mode.
    data_quality_status: Mapped[DataQuality] = mapped_column(
        SAEnum(DataQuality, name="data_quality_enum"),
        default=DataQuality.FULL,
        nullable=False,
    )

    fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("external_id", name="uq_fixture_external_id"),
        Index("ix_fixtures_gameweek", "gameweek_id"),
        Index("ix_fixtures_kickoff", "kickoff_at"),
        Index("ix_fixtures_status", "status"),
    )


class PlayerMatchStats(Base):
    """
    Core fantasy scoring input. One row per player per fixture.

    Stores aggregate stats — not individual event timelines.
    Goals, assists, minutes, cards are the reliable outputs from the
    football-data.org free tier. The raw_data JSONB blob preserves
    the full API response for recomputation if the scoring model changes.

    The scoring job reads this table, computes fantasy_points, then propagates
    up through gameweek_lineup_players → gameweek_lineups → user_gameweek_scores.
    """
    __tablename__ = "player_match_stats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    fixture_id: Mapped[int] = mapped_column(Integer, ForeignKey("fixtures.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=False)

    # Position snapshot at time of match (a player's registered position may differ)
    position_snapshot: Mapped[Position] = mapped_column(
        SAEnum(Position, name="position_enum"), nullable=False
    )

    # Playing time
    started: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    appeared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # started OR subbed on
    minutes_played: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)

    # Scoring events
    goals: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    assists: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    own_goals: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    yellow_cards: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    red_cards: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)

    # Set by scoring job: True if GK/DEF who played 60+ mins and team kept a clean sheet
    clean_sheet: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Computed fantasy points for this fixture (set by scoring job after match ends)
    fantasy_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    data_quality: Mapped[DataQuality] = mapped_column(
        SAEnum(DataQuality, name="data_quality_enum"),
        default=DataQuality.FULL,
        nullable=False,
    )

    # Raw API payload — preserved for audit and recomputation
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    source_last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("player_id", "fixture_id", name="uq_player_match_stats"),
        Index("ix_pms_fixture", "fixture_id"),
        Index("ix_pms_player", "player_id"),
    )
