"""
Fixture browsing routes — authenticated.

Reads from the fixtures already synced into the DB by sync.py.
No external API calls here.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy.orm import aliased

from core.dependencies import CurrentUser, DBSession
from models.competition import Competition
from models.fixture import Fixture
from models.team import Team
from schemas.fixture import FixtureListResponse, FixtureResponse

router = APIRouter()

HomeTeam = aliased(Team)
AwayTeam = aliased(Team)


@router.get("", response_model=FixtureListResponse)
def get_fixtures(
    db: DBSession,
    current_user: CurrentUser,
    competition_code: Optional[str] = Query(default=None, description="PL, PD, BL1, SA, FL1"),
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    status: Optional[str] = Query(default=None, description="SCHEDULED, FINISHED, LIVE, POSTPONED"),
    days_back: int = Query(default=3, ge=0, le=14),
    days_forward: int = Query(default=7, ge=1, le=30),
):
    now = datetime.now(timezone.utc)

    if from_date is None:
        from_date = now - timedelta(days=days_back)
    if to_date is None:
        to_date = now + timedelta(days=days_forward)

    filters = [
        Fixture.kickoff_at >= from_date,
        Fixture.kickoff_at <= to_date,
    ]
    if status:
        filters.append(Fixture.status == status)
    if competition_code:
        comp = db.query(Competition).filter_by(code=competition_code).first()
        if comp:
            filters.append(Fixture.competition_id == comp.id)

    rows = (
        db.query(Fixture, HomeTeam, AwayTeam, Competition)
        .join(HomeTeam, Fixture.home_team_id == HomeTeam.id)
        .join(AwayTeam, Fixture.away_team_id == AwayTeam.id)
        .join(Competition, Fixture.competition_id == Competition.id)
        .filter(*filters)
        .order_by(Fixture.kickoff_at)
        .all()
    )

    fixtures = [
        FixtureResponse(
            id=f.id,
            competition_code=comp.code,
            competition_name=comp.name,
            home_team=home.name,
            home_team_short=home.short_name or home.tla or home.name[:3],
            away_team=away.name,
            away_team_short=away.short_name or away.tla or away.name[:3],
            kickoff_at=f.kickoff_at,
            status=f.status.value if hasattr(f.status, "value") else str(f.status),
            home_score=f.home_score,
            away_score=f.away_score,
        )
        for f, home, away, comp in rows
    ]

    return FixtureListResponse(fixtures=fixtures, total=len(fixtures))
