from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.enums import DataQuality, FixtureStatus, GameweekStatus, ScoringMode


class GameweekResponse(BaseModel):
    id: int
    season_id: int
    number: int
    name: Optional[str]
    deadline_at: datetime
    start_at: datetime
    end_at: datetime
    status: GameweekStatus
    scoring_mode: ScoringMode
    is_current: bool

    model_config = {"from_attributes": True}


class FixtureInGameweekResponse(BaseModel):
    id: int
    competition_id: int
    home_team_id: int
    away_team_id: int
    kickoff_at: Optional[datetime]
    status: FixtureStatus
    home_score: Optional[int]
    away_score: Optional[int]
    data_quality_status: DataQuality

    model_config = {"from_attributes": True}
