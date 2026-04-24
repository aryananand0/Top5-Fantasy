from datetime import datetime
from typing import Optional

from pydantic import BaseModel, computed_field

from models.enums import Position


class PlayerGWScore(BaseModel):
    """Per-player score breakdown inside a gameweek score response."""
    player_id: int
    name: str
    display_name: Optional[str]
    position: Position
    team_name: str
    is_captain: bool
    is_vice_captain: bool
    base_points: int    # Raw fixture points (no 2× applied)
    final_points: int   # After captain/VC multiplier
    points_scored: Optional[int]  # Direct from GameweekLineupPlayer (same as final_points post-score)

    model_config = {"from_attributes": False}


class GameweekScoreResponse(BaseModel):
    """
    A user's score for one gameweek.

    raw_points    = sum of player fantasy points + captain bonus (pre transfer hit)
    transfer_cost = point penalty for extra transfers
    points        = raw_points - transfer_cost  (the final persisted value)
    captain_bonus = extra points earned from the 2× multiplier (captain's base × 1)
    rank_global   = NULL until finalize_gameweek_ranks() is run after all GW matches
    """
    gameweek_id: int
    gameweek_number: int
    gameweek_name: Optional[str]
    points: int                  # Final score (post transfer hit)
    transfer_cost: int
    captain_bonus: int
    rank_global: Optional[int]
    players: list[PlayerGWScore]
    updated_at: datetime

    @computed_field
    @property
    def raw_points(self) -> int:
        return self.points + self.transfer_cost

    model_config = {"from_attributes": False}


class GameweekScoreNotReady(BaseModel):
    """Returned when a gameweek score hasn't been computed yet."""
    gameweek_id: int
    gameweek_number: int
    gameweek_name: Optional[str]
    message: str = "Gameweek scoring has not been completed yet."

    model_config = {"from_attributes": False}
