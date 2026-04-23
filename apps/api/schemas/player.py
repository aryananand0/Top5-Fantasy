from typing import Optional

from pydantic import BaseModel

from models.enums import Position


class PlayerResponse(BaseModel):
    """Player as returned by GET /players — includes current price and team."""
    id: int
    name: str
    display_name: Optional[str]
    position: Position
    team_id: int
    team_name: str
    team_short_name: Optional[str]
    current_price: float
    form_score: float
    starter_confidence: int
    is_available: bool
    availability_note: Optional[str]

    model_config = {"from_attributes": False}


class PlayerListResponse(BaseModel):
    """Paginated player list response."""
    players: list[PlayerResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
