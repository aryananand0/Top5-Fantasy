"""
Gameweek lineup routes — authenticated.

Route design: /api/v1/lineups/current (singular resource, owner = authenticated user).
The "current" qualifier means the lineup for the active season's current gameweek.

Behaviour:
  GET  /lineups/current  — return (or auto-create) the user's lineup for the current GW
  PUT  /lineups/current  — set captain and vice-captain before the GW locks

Auto-creation on GET: if no lineup exists for the current GW, one is created
immediately from the user's active squad snapshot. This means:
  - The user never has to explicitly "create" a lineup
  - Replacing the squad (PUT /squad) deletes the snapshot → next GET rebuilds it
  - After lock, the snapshot is frozen — no further edits possible

Lock gate: PUT returns 403 if is_locked=True or gameweek status >= LOCKED.
"""

from fastapi import APIRouter, HTTPException, status

from core.dependencies import CurrentUser, DBSession
from schemas.lineup import CaptainUpdateRequest, LineupPlayerResponse, LineupResponse
from services.gameweek import get_active_season, get_current_gameweek
from services.lineups.service import (
    delete_lineup_for_squad_gw,
    gameweek_is_editable,
    get_lineup_players,
    get_or_create_lineup,
    sync_lock_state,
    update_captain,
)
from services.squads.service import get_squad_for_user

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_season_and_gw(db: DBSession):
    season = get_active_season(db)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No active season found. Check back soon.",
        )

    gw = get_current_gameweek(db, season.id)
    if not gw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current gameweek found. The season may not have started yet.",
        )

    return season, gw


def _require_squad(db: DBSession, user_id: int, season_id: int):
    squad = get_squad_for_user(db, user_id, season_id)
    if not squad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't built a squad yet. Create one first at POST /squad.",
        )
    return squad


def _build_lineup_response(
    lineup,
    gameweek,
    enriched_players: list,
) -> LineupResponse:
    is_editable = gameweek_is_editable(gameweek) and not lineup.is_locked

    players = [
        LineupPlayerResponse(
            player_id=ep.player.id,
            name=ep.player.name,
            display_name=ep.player.display_name,
            position=ep.player.position,
            team_name=ep.team.name,
            team_short_name=ep.team.short_name,
            current_price=float(ep.player.current_price),
            form_score=float(ep.player.form_score),
            is_available=ep.player.is_available,
            is_captain=ep.player.id == lineup.captain_player_id,
            is_vice_captain=ep.player.id == lineup.vice_captain_player_id,
            points_scored=ep.lineup_player.points_scored,
        )
        for ep in enriched_players
    ]

    return LineupResponse(
        id=lineup.id,
        gameweek_id=gameweek.id,
        gameweek_number=gameweek.number,
        gameweek_name=gameweek.name,
        gameweek_deadline=gameweek.deadline_at,
        gameweek_status=gameweek.status,
        is_locked=lineup.is_locked,
        is_editable=is_editable,
        captain_player_id=lineup.captain_player_id,
        vice_captain_player_id=lineup.vice_captain_player_id,
        players=players,
        points_scored=lineup.points_scored,
        created_at=lineup.created_at,
        updated_at=lineup.updated_at,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/current",
    response_model=LineupResponse,
    summary="Get my current gameweek lineup",
)
def get_current_lineup(db: DBSession, current_user: CurrentUser):
    """
    Returns the authenticated user's lineup for the current gameweek.

    If no lineup exists yet, one is auto-created by snapshotting the active squad.
    The lineup is read-only once the gameweek locks. Use PUT to set captain/VC before then.

    503 if no active season.
    404 if no current gameweek or no squad.
    """
    season, gw = _require_season_and_gw(db)
    squad = _require_squad(db, current_user.id, season.id)

    lineup = get_or_create_lineup(db, squad=squad, gameweek=gw)
    lineup = sync_lock_state(db, lineup, gw)
    enriched = get_lineup_players(db, lineup.id)

    return _build_lineup_response(lineup, gw, enriched)


@router.put(
    "/current",
    response_model=LineupResponse,
    summary="Set captain and vice-captain",
)
def update_current_lineup(
    body: CaptainUpdateRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Set the captain and vice-captain for the current gameweek lineup.

    - Captain earns 2× points for the gameweek.
    - Vice-captain earns 2× only if the captain played 0 minutes.
    - Both must be in your 11-player lineup.
    - They cannot be the same player.

    Returns 403 if the gameweek has locked.
    Returns 400 if validation fails.
    Returns 404 if no squad or no current gameweek.
    """
    season, gw = _require_season_and_gw(db)
    squad = _require_squad(db, current_user.id, season.id)

    lineup = get_or_create_lineup(db, squad=squad, gameweek=gw)
    lineup = sync_lock_state(db, lineup, gw)

    if lineup.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Gameweek {gw.number} has locked. "
                "Captain and vice-captain can no longer be changed."
            ),
        )

    enriched = get_lineup_players(db, lineup.id)
    lineup_player_ids = {ep.player.id for ep in enriched}

    lineup, errors = update_captain(
        db,
        lineup=lineup,
        captain_player_id=body.captain_player_id,
        vice_captain_player_id=body.vice_captain_player_id,
        lineup_player_ids=lineup_player_ids,
    )
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": [str(e) for e in errors]},
        )

    # Re-fetch enriched players after update (captain/vc flags now correct)
    enriched = get_lineup_players(db, lineup.id)
    return _build_lineup_response(lineup, gw, enriched)
