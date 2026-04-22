from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum as SAEnum, ForeignKey, Index,
    Integer, SmallInteger, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin
from .enums import GameweekStatus, ScoringMode


class Gameweek(Base, TimestampMixin):
    """
    App-defined gameweeks — not tied to individual league matchdays.
    One GW covers a window of matches across all 5 competitions.
    """
    __tablename__ = "gameweeks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"), nullable=False)
    number: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1, 2, 3 ...
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "Gameweek 1"

    # Deadline: when transfers lock and lineups are frozen
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # start_at / end_at: first and last kickoff in this GW window
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[GameweekStatus] = mapped_column(
        SAEnum(GameweekStatus, name="gameweek_status_enum"),
        default=GameweekStatus.UPCOMING,
        nullable=False,
    )

    # Explicit scoring mode set per GW based on data availability from football-data.org.
    # RICH = minutes, assists, cards, clean sheets all available.
    # FALLBACK = goals and result only; partial bonus points skipped.
    scoring_mode: Mapped[ScoringMode] = mapped_column(
        SAEnum(ScoringMode, name="scoring_mode_enum"),
        default=ScoringMode.RICH,
        nullable=False,
    )

    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("season_id", "number", name="uq_gameweek_season_number"),
        Index("ix_gameweeks_season_status", "season_id", "status"),
    )
