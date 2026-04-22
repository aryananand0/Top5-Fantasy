from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum as SAEnum, ForeignKey, Index, Integer,
    Numeric, SmallInteger, String, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin
from .enums import Position


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    position: Mapped[Position] = mapped_column(SAEnum(Position, name="position_enum"), nullable=False)

    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=False)
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"), nullable=False)

    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # football-data.org
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # TheSportsDB enrichment
    nationality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # --- Custom pricing ---
    # base_price: set at season start using position + club strength + prior form
    # current_price: updated each gameweek by the pricing engine
    base_price: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)
    current_price: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)

    # Pricing engine inputs (updated by background jobs)
    starter_confidence: Mapped[int] = mapped_column(SmallInteger, default=3, nullable=False)  # 1–5
    form_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)

    # Availability
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    availability_note: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    __table_args__ = (
        UniqueConstraint("external_id", "season_id", name="uq_player_external_season"),
        Index("ix_players_team_season", "team_id", "season_id"),
        Index("ix_players_position", "position"),
        Index("ix_players_current_price", "current_price"),
    )


class PriceHistory(Base):
    """Weekly price snapshot per player. One row per player per gameweek."""
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    gameweek_id: Mapped[int] = mapped_column(Integer, ForeignKey("gameweeks.id"), nullable=False)

    old_price: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)
    new_price: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)
    # Signed: +0.5 means price rose, -0.5 means fell
    change_amount: Mapped[float] = mapped_column(Numeric(4, 1), default=0.0, nullable=False)
    reason_summary: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("player_id", "gameweek_id", name="uq_price_history_player_gw"),
        Index("ix_price_history_player", "player_id"),
    )
