from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Index,
    Integer, Numeric, SmallInteger, String, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Squad(Base, TimestampMixin):
    """
    A user's season-long squad. One per user per season.

    budget_remaining: starts at 100.0, decreases/increases with transfers.
    free_transfers_banked: carries over each GW (max 3). Starts at 1 for GW1
    because the initial squad pick is free, and users earn their first 2
    on the GW1 rollover.
    total_points: running season total, updated after each GW finalises.
    overall_rank: updated in bulk after each GW finalises.
    """
    __tablename__ = "squads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    budget_remaining: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)  # starts at 100.0
    free_transfers_banked: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)  # max 3

    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "season_id", name="uq_squad_user_season"),
    )


class SquadPlayer(Base):
    """
    A player who is or was in a user's squad this season.

    is_active=True means they are currently in the squad.
    is_active=False means they were sold in a transfer.

    purchase_price: price paid when the player was bought. Used for budget tracking.
    Sell price is always players.current_price at time of sale — no FPL-style profit split in MVP.

    joined_gameweek_id / left_gameweek_id: used for transfer history display.
    """
    __tablename__ = "squad_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    squad_id: Mapped[int] = mapped_column(Integer, ForeignKey("squads.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)

    purchase_price: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)

    joined_gameweek_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("gameweeks.id"), nullable=True
    )
    left_gameweek_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("gameweeks.id"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_squad_players_squad_active", "squad_id", "is_active"),
        Index("ix_squad_players_player", "player_id"),
    )
