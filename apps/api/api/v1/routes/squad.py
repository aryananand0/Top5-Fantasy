"""
Squad routes — authenticated.

Route decision: /api/v1/squad (singular, implicit owner = current user).
Cleaner than /me/squad for mobile SDK use and matches the "one squad per user
per season" invariant — there is no collection to list.

Behavior:
  GET  /squad  — return current user's squad for the active season
  POST /squad  — create squad (once per season; 409 if already exists)
  PUT  /squad  — replace squad (allowed only before season locks; 403 after)
"""

from fastapi import APIRouter, HTTPException, status

from core.dependencies import CurrentUser, DBSession
from schemas.squad import SquadCreateRequest, SquadResponse, SquadPlayerResponse
from services.gameweek import get_current_gameweek
from services.lineups.service import delete_lineup_for_squad_gw
from services.squads.service import (
    create_squad,
    get_active_season,
    get_squad_detail,
    get_squad_for_user,
    replace_squad,
    season_is_locked,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_squad_response(detail) -> SquadResponse:
    """Convert a SquadDetail into the API response shape."""
    players = [
        SquadPlayerResponse(
            player_id=m.player.id,
            name=m.player.name,
            display_name=m.player.display_name,
            position=m.player.position,
            team_id=m.team.id,
            team_name=m.team.name,
            purchase_price=float(m.squad_player.purchase_price),
            current_price=float(m.player.current_price),
            form_score=float(m.player.form_score),
            starter_confidence=m.player.starter_confidence,
            is_available=m.player.is_available,
        )
        for m in detail.members
    ]
    s = detail.squad
    return SquadResponse(
        id=s.id,
        name=s.name,
        budget_remaining=float(s.budget_remaining),
        total_cost=detail.total_cost,
        total_points=s.total_points,
        overall_rank=s.overall_rank,
        free_transfers_banked=s.free_transfers_banked,
        created_at=s.created_at,
        updated_at=s.updated_at,
        players=players,
    )


def _require_active_season(db: DBSession):
    season = get_active_season(db)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No active season found. Check back soon.",
        )
    return season


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=SquadResponse,
    summary="Get my squad",
)
def get_squad(db: DBSession, current_user: CurrentUser):
    """
    Returns the authenticated user's squad for the active season.
    404 if no squad has been created yet.
    """
    season = _require_active_season(db)
    squad = get_squad_for_user(db, current_user.id, season.id)
    if not squad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't built a squad yet. Use POST /squad to create one.",
        )
    return _build_squad_response(get_squad_detail(db, squad))


@router.post(
    "",
    response_model=SquadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create my squad",
)
def create_my_squad(
    body: SquadCreateRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Create a new squad for the active season.
    Returns 409 if a squad already exists — use PUT to replace it.
    Returns 400 with an errors list if squad rules are violated.
    """
    season = _require_active_season(db)

    existing = get_squad_for_user(db, current_user.id, season.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a squad this season. Use PUT /squad to replace it.",
        )

    squad_name = body.name or f"{current_user.display_name or current_user.username}'s Squad"

    detail, errors = create_squad(
        db,
        user_id=current_user.id,
        season_id=season.id,
        player_ids=body.player_ids,
        squad_name=squad_name,
    )
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": [str(e) for e in errors]},
        )

    return _build_squad_response(detail)


@router.put(
    "",
    response_model=SquadResponse,
    summary="Replace my squad",
)
def replace_my_squad(
    body: SquadCreateRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Fully replace the active squad with a new 11-player selection.

    Allowed only while the season is unlocked (no gameweek is LOCKED or beyond).
    After the first gameweek locks, use the transfer system instead.

    Old squad_players are soft-deleted to preserve history.
    Returns 400 with an errors list if squad rules are violated.
    Returns 403 if the season is already locked.
    Returns 404 if no squad exists yet — use POST first.
    """
    season = _require_active_season(db)

    squad = get_squad_for_user(db, current_user.id, season.id)
    if not squad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No squad found. Use POST /squad to create one first.",
        )

    if season_is_locked(db, season.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "The season has started. Full squad replacement is no longer allowed. "
                "Use the transfer system to make changes."
            ),
        )

    detail, errors = replace_squad(
        db,
        squad=squad,
        player_ids=body.player_ids,
        season_id=season.id,
    )
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": [str(e) for e in errors]},
        )

    # Invalidate any existing lineup snapshot for the current GW so the
    # next GET /lineups/current creates a fresh one from the new squad.
    current_gw = get_current_gameweek(db, season.id)
    if current_gw:
        delete_lineup_for_squad_gw(db, squad_id=squad.id, gameweek_id=current_gw.id)

    return _build_squad_response(detail)
