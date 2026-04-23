"""
Transfer routes — authenticated.

Route design:
  GET  /transfers/summary         — current GW transfer state for the user
  POST /transfers/preview         — preview without applying
  POST /transfers/apply           — apply transfers atomically
  GET  /transfers/history         — paginated past transfers

All routes use the active season's current gameweek.
Transfers are blocked when the current gameweek is LOCKED or beyond.
"""

import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from core.dependencies import CurrentUser, DBSession
from schemas.squad import SquadPlayerResponse, SquadResponse
from schemas.transfer import (
    PlayerBriefResponse,
    TransferApplyRequest,
    TransferApplyResponse,
    TransferHistoryItemResponse,
    TransferHistoryResponse,
    TransferPairPreview,
    TransferPreviewRequest,
    TransferPreviewResponse,
    TransferSummaryResponse,
)
from services.gameweek import get_active_season, get_current_gameweek
from services.squads.service import get_squad_detail, get_squad_for_user
from services.transfers.constants import POINTS_PER_EXTRA_TRANSFER
from services.transfers.service import (
    apply_transfers,
    get_transfer_history,
    get_transfers_for_squad_gw,
    preview_transfers,
)

router = APIRouter()

_LOCKED_STATUSES = {"LOCKED", "ACTIVE", "SCORING", "FINISHED"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_season_gw_squad(db: DBSession, user_id: int):
    """Shared setup: get season, current GW, and squad. Raise on any missing."""
    season = get_active_season(db)
    if not season:
        raise HTTPException(status_code=503, detail="No active season found.")

    gw = get_current_gameweek(db, season.id)
    if not gw:
        raise HTTPException(status_code=404, detail="No current gameweek found.")

    squad = get_squad_for_user(db, user_id, season.id)
    if not squad:
        raise HTTPException(
            status_code=404,
            detail="You haven't built a squad yet. Create one at POST /squad.",
        )

    return season, gw, squad


def _gw_is_editable(gw) -> bool:
    from models.enums import GameweekStatus
    locked = {GameweekStatus.LOCKED, GameweekStatus.ACTIVE, GameweekStatus.SCORING, GameweekStatus.FINISHED}
    return gw.status not in locked


def _build_pair_preview(pair_detail) -> TransferPairPreview:
    return TransferPairPreview(
        player_out=PlayerBriefResponse(
            id=pair_detail.player_out.id,
            name=pair_detail.player_out.name,
            display_name=pair_detail.player_out.display_name,
            position=pair_detail.player_out.position,
            team_name=pair_detail.player_out.team_name,
            team_short_name=pair_detail.player_out.team_short_name,
            current_price=pair_detail.player_out.current_price,
        ),
        player_in=PlayerBriefResponse(
            id=pair_detail.player_in.id,
            name=pair_detail.player_in.name,
            display_name=pair_detail.player_in.display_name,
            position=pair_detail.player_in.position,
            team_name=pair_detail.player_in.team_name,
            team_short_name=pair_detail.player_in.team_short_name,
            current_price=pair_detail.player_in.current_price,
        ),
        price_out=pair_detail.price_out,
        price_in=pair_detail.price_in,
        budget_delta=round(pair_detail.price_out - pair_detail.price_in, 1),
        is_free=pair_detail.is_free,
        point_cost=pair_detail.point_cost,
    )


def _build_squad_response(detail) -> SquadResponse:
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/summary",
    response_model=TransferSummaryResponse,
    summary="Current gameweek transfer status",
)
def get_transfer_summary(db: DBSession, current_user: CurrentUser):
    """
    Returns the current gameweek transfer state for the authenticated user:
    free transfers available, transfers made this GW, point cost, lock status.
    """
    season, gw, squad = _require_season_gw_squad(db, current_user.id)

    transfers_this_gw = get_transfers_for_squad_gw(db, squad.id, gw.id)
    points_hit = sum(t.point_cost for t in transfers_this_gw)
    is_editable = _gw_is_editable(gw)

    return TransferSummaryResponse(
        gameweek_id=gw.id,
        gameweek_number=gw.number,
        gameweek_name=gw.name,
        gameweek_deadline=gw.deadline_at,
        gameweek_status=gw.status.value,
        is_editable=is_editable,
        free_transfers_available=squad.free_transfers_banked,
        transfers_made_this_gw=len(transfers_this_gw),
        points_hit_this_gw=points_hit,
        budget_remaining=float(squad.budget_remaining),
    )


@router.post(
    "/preview",
    response_model=TransferPreviewResponse,
    summary="Preview transfer(s) without applying",
)
def preview_transfer(
    body: TransferPreviewRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Preview 1–5 transfer pairs as a batch.

    Returns budget impact, points hit, and validation errors — does NOT modify data.
    Use this to show the user what will happen before they confirm.

    Still returns 200 even when errors exist — check the `errors` field.
    """
    season, gw, squad = _require_season_gw_squad(db, current_user.id)

    if not _gw_is_editable(gw):
        return TransferPreviewResponse(
            gameweek_id=gw.id,
            gameweek_number=gw.number,
            is_editable=False,
            transfers=[],
            budget_before=float(squad.budget_remaining),
            budget_after=float(squad.budget_remaining),
            total_points_hit=0,
            free_transfers_before=squad.free_transfers_banked,
            free_transfers_after=squad.free_transfers_banked,
            is_valid=False,
            errors=[f"Gameweek {gw.number} has locked. Transfers are no longer allowed."],
        )

    pairs = [(t.player_out_id, t.player_in_id) for t in body.transfers]
    result = preview_transfers(db, squad=squad, gameweek=gw, season_id=season.id, pairs=pairs)

    errors = [str(e) for e in result.transfer_errors] + [str(e) for e in result.squad_errors]

    return TransferPreviewResponse(
        gameweek_id=gw.id,
        gameweek_number=gw.number,
        is_editable=True,
        transfers=[_build_pair_preview(p) for p in result.pairs],
        budget_before=result.budget_before,
        budget_after=result.budget_after,
        total_points_hit=result.total_points_hit,
        free_transfers_before=result.free_transfers_before,
        free_transfers_after=result.free_transfers_after,
        is_valid=result.is_valid,
        errors=errors,
    )


@router.post(
    "/apply",
    response_model=TransferApplyResponse,
    summary="Apply transfer(s)",
)
def apply_transfer(
    body: TransferApplyRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Apply 1–5 transfer pairs atomically.

    Returns 403 if the gameweek is locked.
    Returns 400 if validation fails (errors list included).
    On success, returns the updated squad and transfer summary.
    """
    season, gw, squad = _require_season_gw_squad(db, current_user.id)

    if not _gw_is_editable(gw):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Gameweek {gw.number} has locked. Transfers are no longer allowed.",
        )

    pairs = [(t.player_out_id, t.player_in_id) for t in body.transfers]
    records, preview = apply_transfers(
        db, squad=squad, gameweek=gw, season_id=season.id, pairs=pairs
    )

    if not preview.is_valid:
        errors = [str(e) for e in preview.transfer_errors] + [str(e) for e in preview.squad_errors]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors},
        )

    transfers_this_gw = get_transfers_for_squad_gw(db, squad.id, gw.id)
    updated_detail = get_squad_detail(db, squad)

    return TransferApplyResponse(
        applied_transfers=[_build_pair_preview(p) for p in preview.pairs],
        squad=_build_squad_response(updated_detail),
        total_points_hit=preview.total_points_hit,
        free_transfers_remaining=squad.free_transfers_banked,
        transfers_this_gw=len(transfers_this_gw),
    )


@router.get(
    "/history",
    response_model=TransferHistoryResponse,
    summary="Transfer history for the authenticated user",
)
def get_transfer_history_route(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=50),
):
    """
    Returns past transfers for the user's squad, newest first.
    Includes player names for display convenience.
    """
    season = get_active_season(db)
    if not season:
        raise HTTPException(status_code=503, detail="No active season found.")

    squad = get_squad_for_user(db, current_user.id, season.id)
    if not squad:
        return TransferHistoryResponse(transfers=[], total=0, page=1, per_page=per_page, total_pages=1)

    from sqlalchemy import select
    from models.player import Player
    from models.transfer import Transfer

    transfers, total = get_transfer_history(db, squad.id, page=page, per_page=per_page)

    # Build player name lookup
    all_player_ids = {t.player_in_id for t in transfers} | {t.player_out_id for t in transfers}
    from services.gameweek import list_gameweeks
    gws = {gw.id: gw for gw in list_gameweeks(db, season.id)}

    player_rows = db.execute(
        select(Player).where(Player.id.in_(all_player_ids))
    ).scalars().all()
    player_names = {p.id: (p.display_name or p.name) for p in player_rows}

    items = [
        TransferHistoryItemResponse(
            id=t.id,
            gameweek_number=gws[t.gameweek_id].number if t.gameweek_id in gws else 0,
            player_out_id=t.player_out_id,
            player_out_name=player_names.get(t.player_out_id, f"Player {t.player_out_id}"),
            player_in_id=t.player_in_id,
            player_in_name=player_names.get(t.player_in_id, f"Player {t.player_in_id}"),
            price_out=float(t.price_out),
            price_in=float(t.price_in),
            is_free=t.is_free,
            point_cost=t.point_cost,
            created_at=t.created_at,
        )
        for t in transfers
    ]

    return TransferHistoryResponse(
        transfers=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=math.ceil(total / per_page) if total > 0 else 1,
    )
