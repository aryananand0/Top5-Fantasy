from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.enums import Position


class SquadCreateRequest(BaseModel):
    """Payload for POST /squad and PUT /squad."""
    player_ids: list[int] = Field(
        min_length=1,
        description="Ordered list of 11 player IDs.",
    )
    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional squad name. Defaults to '{username}'s Squad'.",
    )


class SquadPlayerResponse(BaseModel):
    """One player in a squad, enriched with player + team data."""
    player_id: int
    name: str
    display_name: Optional[str]
    position: Position
    team_id: int
    team_name: str
    purchase_price: float
    current_price: float
    form_score: float
    starter_confidence: int
    is_available: bool

    model_config = {"from_attributes": False}


class SquadResponse(BaseModel):
    """Full squad response returned by GET, POST, and PUT /squad."""
    id: int
    name: str
    budget_remaining: float
    total_cost: float
    total_points: int
    overall_rank: Optional[int]
    free_transfers_banked: int
    created_at: datetime
    updated_at: datetime
    players: list[SquadPlayerResponse]

    model_config = {"from_attributes": False}


class SquadValidationErrorResponse(BaseModel):
    """Returned when squad validation fails (HTTP 400)."""
    detail: str = "Squad validation failed."
    errors: list[str]
