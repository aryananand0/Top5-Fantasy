"""
Player browsing routes — authenticated.

Provides the player pool for the squad builder. Returns players with their
current prices, team, and availability so the frontend can render the
player browser and filter/search.

All routes require auth — the player catalog is not a public endpoint.
"""

from typing import Optional
import math

from fastapi import APIRouter, HTTPException, Query, status

from core.dependencies import CurrentUser, DBSession
from models.enums import Position
from schemas.player import PlayerListResponse, PlayerResponse
from services.gameweek import get_active_season
from services.squads.service import list_players

router = APIRouter()


@router.get(
    "",
    response_model=PlayerListResponse,
    summary="Browse available players",
)
def get_players(
    db: DBSession,
    current_user: CurrentUser,
    position: Optional[Position] = Query(default=None, description="Filter by position: GK, DEF, MID, FWD"),
    team_id: Optional[int] = Query(default=None, description="Filter by team ID"),
    search: Optional[str] = Query(default=None, max_length=100, description="Search by player name"),
    available_only: bool = Query(default=True, description="Exclude unavailable players"),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=200, description="Players per page"),
):
    """
    Returns a paginated list of players for the active season.

    Use for building the squad browser in the UI. Supports filtering by
    position, team, and name search. Results are sorted by position, then
    price descending (most expensive first within each position).
    """
    season = get_active_season(db)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No active season found.",
        )

    rows, total = list_players(
        db,
        season.id,
        position=position,
        team_id=team_id,
        search=search,
        available_only=available_only,
        page=page,
        per_page=per_page,
    )

    players = [
        PlayerResponse(
            id=player.id,
            name=player.name,
            display_name=player.display_name,
            position=player.position,
            team_id=team.id,
            team_name=team.name,
            team_short_name=team.short_name,
            current_price=float(player.current_price),
            form_score=float(player.form_score),
            starter_confidence=player.starter_confidence,
            is_available=player.is_available,
            availability_note=player.availability_note,
        )
        for player, team in rows
    ]

    return PlayerListResponse(
        players=players,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=math.ceil(total / per_page) if total > 0 else 1,
    )
