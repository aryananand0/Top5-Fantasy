from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # football-data.org codes: PL, PD, BL1, SA, FL1
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # football-data.org ID
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # TheSportsDB enrichment

    # Competitions are stable across seasons — no season_id needed here.
    # Season context lives on players and fixtures.
