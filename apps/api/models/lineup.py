from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, SmallInteger, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class GameweekLineup(Base, TimestampMixin):
    """
    A user's active selection for a specific gameweek.

    Created when a user first saves their lineup for a GW (or auto-created at deadline
    from their current squad if they haven't made a selection).

    is_locked flips to True at the GW deadline. After that, no changes are allowed.
    locked_at records the exact moment of locking (system deadline, not user action).

    captain_player_id / vice_captain_player_id: must be in the 11 players.
    Vice-captain becomes active captain only if captain did not appear (0 minutes).

    points_scored: total GW points for this user, set by the scoring job.
    transfer_cost_applied: penalty points for extra transfers above free allowance.
    """
    __tablename__ = "gameweek_lineups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    squad_id: Mapped[int] = mapped_column(Integer, ForeignKey("squads.id"), nullable=False)
    gameweek_id: Mapped[int] = mapped_column(Integer, ForeignKey("gameweeks.id"), nullable=False)

    captain_player_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("players.id"), nullable=True
    )
    vice_captain_player_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("players.id"), nullable=True
    )

    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Set by scoring job after all GW matches finish
    points_scored: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    transfer_cost_applied: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("squad_id", "gameweek_id", name="uq_lineup_squad_gameweek"),
        Index("ix_lineups_gameweek", "gameweek_id"),
    )


class GameweekLineupPlayer(Base):
    """
    The 11 players in a gameweek lineup.

    points_scored: individual player's fantasy points for this GW (including captain 2x).
    Set by the scoring job — used for the per-player breakdown UI.
    """
    __tablename__ = "gameweek_lineup_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lineup_id: Mapped[int] = mapped_column(Integer, ForeignKey("gameweek_lineups.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)

    points_scored: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("lineup_id", "player_id", name="uq_lineup_player"),
        Index("ix_glp_lineup", "lineup_id"),
    )
