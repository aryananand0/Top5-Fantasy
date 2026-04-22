from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Index,
    Integer, Numeric, SmallInteger, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Transfer(Base):
    """
    One row = one player in + one player out.

    price_in: price paid for the incoming player at time of transfer.
    price_out: sell value of the outgoing player at time of transfer
               (= players.current_price at that moment in MVP — no profit split).

    is_free: True if consumed from free_transfers_banked. False = costs 4 points.
    point_cost: 0 if free, 4 if not. Stored to avoid recalculation.
    """
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    squad_id: Mapped[int] = mapped_column(Integer, ForeignKey("squads.id"), nullable=False)
    gameweek_id: Mapped[int] = mapped_column(Integer, ForeignKey("gameweeks.id"), nullable=False)

    player_in_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    player_out_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)

    price_in: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)
    price_out: Mapped[float] = mapped_column(Numeric(6, 1), nullable=False)

    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False)
    point_cost: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_transfers_squad_gameweek", "squad_id", "gameweek_id"),
        Index("ix_transfers_player_in", "player_in_id"),
        Index("ix_transfers_player_out", "player_out_id"),
    )
