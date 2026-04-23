from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.enums import GameweekStatus, Position


class LineupPlayerResponse(BaseModel):
    """One player in the gameweek lineup."""
    player_id: int
    name: str
    display_name: Optional[str]
    position: Position
    team_name: str
    team_short_name: str
    current_price: float
    form_score: float
    is_available: bool
    is_captain: bool
    is_vice_captain: bool
    points_scored: Optional[int]  # filled by scoring job; null until then

    model_config = {"from_attributes": False}


class LineupResponse(BaseModel):
    """
    Full lineup response — returned by GET and PUT /lineups/current.

    is_editable: convenience flag the frontend uses to enable/disable the picker.
    It is False when gameweek_status is LOCKED, ACTIVE, SCORING, or FINISHED,
    or when the lineup's own is_locked flag is True.
    """
    id: int
    gameweek_id: int
    gameweek_number: int
    gameweek_name: str
    gameweek_deadline: datetime
    gameweek_status: GameweekStatus
    is_locked: bool
    is_editable: bool
    captain_player_id: Optional[int]
    vice_captain_player_id: Optional[int]
    players: list[LineupPlayerResponse]
    points_scored: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": False}


class CaptainUpdateRequest(BaseModel):
    """Payload for PUT /lineups/current — set captain and vice-captain."""
    captain_player_id: int = Field(description="Player ID to assign as captain (2× points).")
    vice_captain_player_id: int = Field(
        description="Player ID to assign as vice-captain. "
                    "Active only if captain did not appear (0 minutes played)."
    )


class LineupValidationErrorResponse(BaseModel):
    """Returned when captain/vc validation fails (HTTP 400)."""
    detail: str = "Lineup validation failed."
    errors: list[str]
