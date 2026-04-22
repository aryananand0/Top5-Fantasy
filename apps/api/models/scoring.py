from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Index, Integer,
    SmallInteger, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserGameweekScore(Base):
    """
    Final fantasy score for a user in a specific gameweek.

    Written by the scoring job after all fixtures in the GW are finished
    and points have been calculated. One row per user per gameweek.

    Kept separate from gameweek_lineups so leaderboard queries are simple:
    SELECT * FROM user_gameweek_scores WHERE gameweek_id = ? ORDER BY points DESC

    rank_global: set in bulk after all scores are computed for the GW.
                 NULL until the GW is fully scored.

    captain_points: the bonus points earned specifically from the captain (2x multiplier
                    contribution above base). Stored for "highest captain" stats.
    """
    __tablename__ = "user_gameweek_scores"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    squad_id: Mapped[int] = mapped_column(Integer, ForeignKey("squads.id"), nullable=False)
    gameweek_id: Mapped[int] = mapped_column(Integer, ForeignKey("gameweeks.id"), nullable=False)
    lineup_id: Mapped[int] = mapped_column(Integer, ForeignKey("gameweek_lineups.id"), nullable=False)

    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    transfer_cost: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    captain_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    rank_global: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "gameweek_id", name="uq_user_gw_score"),
        Index("ix_ugws_gameweek_points", "gameweek_id", "points"),  # leaderboard queries
        Index("ix_ugws_squad", "squad_id"),
    )
