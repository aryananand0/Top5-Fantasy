from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Index,
    Integer, SmallInteger, String, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MiniLeague(Base):
    """
    A private or public fantasy league users can create and invite others to.

    code: short invite code (e.g. "T5F-X9K2") used in invitation URLs.
    owner_user_id: the user who created the league; they can rename/delete it.
    max_members: NULL means no cap.
    is_public: if True, appears in the public league directory (future feature).
    """
    __tablename__ = "mini_leagues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    owner_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    max_members: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LeagueMember(Base):
    """
    A user's membership in a mini-league.

    Keyed on user_id (not squad_id) because:
    - The user is the social identity
    - One user has one active squad per season anyway
    - Invite/admin logic centres on users

    To get a member's standings, join to squads via user_id + season_id.
    """
    __tablename__ = "league_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    league_id: Mapped[int] = mapped_column(Integer, ForeignKey("mini_leagues.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("league_id", "user_id", name="uq_league_member"),
        Index("ix_league_members_league", "league_id"),
        Index("ix_league_members_user", "user_id"),
    )
