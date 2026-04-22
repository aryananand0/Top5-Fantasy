"""
Gameweek read routes.

All routes are read-only. Gameweeks are created and managed via admin scripts,
not through the API. Write operations (generate, assign, refresh) happen via
scripts/gameweeks.py.
"""

from fastapi import APIRouter, HTTPException, status

from core.dependencies import DBSession
from schemas.gameweek import FixtureInGameweekResponse, GameweekResponse
from services.gameweek import (
    get_active_season,
    get_current_gameweek,
    get_gameweek_by_id,
    get_gameweek_fixtures,
    list_gameweeks,
)

router = APIRouter()


@router.get(
    "/current",
    response_model=GameweekResponse,
    summary="Get the current gameweek",
)
def current_gameweek(db: DBSession):
    """
    Returns the gameweek flagged is_current=True for the active season.
    This is the primary endpoint for the frontend to determine the active game loop.
    """
    season = get_active_season(db)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active season found.",
        )
    gw = get_current_gameweek(db, season.id)
    if not gw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current gameweek. Run 'python scripts/gameweeks.py refresh' to set one.",
        )
    return gw


@router.get(
    "",
    response_model=list[GameweekResponse],
    summary="List all gameweeks for the active season",
)
def gameweeks_list(db: DBSession):
    season = get_active_season(db)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active season found.",
        )
    return list_gameweeks(db, season.id)


@router.get(
    "/{gw_id}",
    response_model=GameweekResponse,
    summary="Get a gameweek by ID",
)
def gameweek_detail(gw_id: int, db: DBSession):
    gw = get_gameweek_by_id(db, gw_id)
    if not gw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gameweek not found.",
        )
    return gw


@router.get(
    "/{gw_id}/fixtures",
    response_model=list[FixtureInGameweekResponse],
    summary="List fixtures assigned to a gameweek",
)
def gameweek_fixtures(gw_id: int, db: DBSession):
    gw = get_gameweek_by_id(db, gw_id)
    if not gw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gameweek not found.",
        )
    return get_gameweek_fixtures(db, gw_id)
