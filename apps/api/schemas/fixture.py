from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FixtureResponse(BaseModel):
    id: int
    competition_code: str
    competition_name: str
    home_team: str
    home_team_short: str
    away_team: str
    away_team_short: str
    kickoff_at: Optional[datetime]
    status: str
    home_score: Optional[int]
    away_score: Optional[int]


class FixtureListResponse(BaseModel):
    fixtures: list[FixtureResponse]
    total: int
