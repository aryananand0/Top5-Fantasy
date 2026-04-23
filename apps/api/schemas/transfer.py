from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from schemas.squad import SquadResponse


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class TransferPairRequest(BaseModel):
    """One player out + one player in."""
    player_out_id: int = Field(description="ID of the player to remove from your squad.")
    player_in_id: int = Field(description="ID of the replacement player to add.")


class TransferPreviewRequest(BaseModel):
    """Preview 1–5 transfer pairs without applying them."""
    transfers: list[TransferPairRequest] = Field(
        min_length=1,
        max_length=5,
        description="Up to 5 transfer pairs to preview as a batch.",
    )


class TransferApplyRequest(BaseModel):
    """Apply 1–5 transfer pairs atomically."""
    transfers: list[TransferPairRequest] = Field(
        min_length=1,
        max_length=5,
        description="Up to 5 transfer pairs to apply.",
    )


# ---------------------------------------------------------------------------
# Shared sub-objects
# ---------------------------------------------------------------------------

class PlayerBriefResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str]
    position: str
    team_name: str
    team_short_name: str
    current_price: float

    model_config = {"from_attributes": False}


class TransferPairPreview(BaseModel):
    """One transfer pair with prices and cost information."""
    player_out: PlayerBriefResponse
    player_in: PlayerBriefResponse
    price_out: float
    price_in: float
    budget_delta: float     # price_out - price_in (positive = profit, negative = cost)
    is_free: bool
    point_cost: int

    model_config = {"from_attributes": False}


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class TransferPreviewResponse(BaseModel):
    """
    What would happen if these transfers were applied.

    If errors is non-empty, nothing should be applied.
    is_valid: convenience flag — True when errors is empty.
    """
    gameweek_id: int
    gameweek_number: int
    is_editable: bool
    transfers: list[TransferPairPreview]
    budget_before: float
    budget_after: float
    total_points_hit: int
    free_transfers_before: int
    free_transfers_after: int
    is_valid: bool
    errors: list[str]

    model_config = {"from_attributes": False}


class TransferApplyResponse(BaseModel):
    """
    Confirmation after transfers are applied.

    Returns the updated squad alongside the applied transfer details
    so the frontend can update all views in one response.
    """
    applied_transfers: list[TransferPairPreview]
    squad: SquadResponse
    total_points_hit: int
    free_transfers_remaining: int
    transfers_this_gw: int

    model_config = {"from_attributes": False}


class TransferSummaryResponse(BaseModel):
    """
    Current gameweek transfer status for the authenticated user.
    Returned by GET /transfers/summary.
    """
    gameweek_id: int
    gameweek_number: int
    gameweek_name: str
    gameweek_deadline: datetime
    gameweek_status: str
    is_editable: bool
    free_transfers_available: int
    transfers_made_this_gw: int
    points_hit_this_gw: int
    budget_remaining: float

    model_config = {"from_attributes": False}


class TransferHistoryItemResponse(BaseModel):
    """One past transfer record."""
    id: int
    gameweek_number: int
    player_out_id: int
    player_out_name: str
    player_in_id: int
    player_in_name: str
    price_out: float
    price_in: float
    is_free: bool
    point_cost: int
    created_at: datetime

    model_config = {"from_attributes": False}


class TransferHistoryResponse(BaseModel):
    transfers: list[TransferHistoryItemResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = {"from_attributes": False}
