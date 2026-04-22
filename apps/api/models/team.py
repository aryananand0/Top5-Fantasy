from typing import Optional

from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tla: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # e.g. "ARS", "BAR"

    # Teams are stable club identities — not duplicated per season.
    # Promotion/relegation is handled by updating competition_id if necessary.
    competition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitions.id"), nullable=False, index=True
    )

    external_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, nullable=True)  # football-data.org
    badge_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # TheSportsDB enrichment

    # 1 (weakest) to 5 (strongest) — used as a pricing input
    strength: Mapped[int] = mapped_column(SmallInteger, default=3, nullable=False)
