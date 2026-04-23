"""
Transfer service — DB operations for the transfer system.

Key design decisions (MVP):

1. Multi-transfer support: up to MAX_TRANSFERS_PER_REQUEST pairs per request.
   The full batch is validated as a unit and applied atomically so the squad
   is always left in a valid state.

2. Position rule: no like-for-like requirement. The projected squad after all
   transfers must satisfy the full squad rules (position counts, budget, club
   limit). This supports flexible multi-transfer scenarios naturally.

3. Banking: free_transfers_banked on Squad is decremented per apply. A separate
   rollover_free_transfers() is called once per GW deadline (via script) to
   credit the new allocation.

4. Lineup interaction: applying transfers deletes the current GW lineup snapshot
   (same rule as replacing the full squad). The next GET /lineups/current
   creates a fresh snapshot from the updated squad.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import GameweekStatus
from models.gameweek import Gameweek
from models.lineup import GameweekLineup, GameweekLineupPlayer
from models.player import Player
from models.squad import Squad, SquadPlayer
from models.team import Team
from models.transfer import Transfer
from services.squads.constants import BUDGET_CAP
from services.squads.service import get_squad_detail
from services.squads.validation import SquadError, validate_squad
from services.transfers.constants import MAX_FREE_TRANSFERS_BANKED, POINTS_PER_EXTRA_TRANSFER
from services.transfers.validation import (
    TransferError,
    compute_points_hit,
    validate_transfer_pairs,
)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class PlayerBrief:
    id: int
    name: str
    display_name: Optional[str]
    position: str
    team_name: str
    team_short_name: str
    current_price: float


@dataclass
class TransferPairDetail:
    player_out: PlayerBrief
    player_in: PlayerBrief
    price_out: float
    price_in: float
    is_free: bool
    point_cost: int


@dataclass
class TransferPreviewResult:
    pairs: list[TransferPairDetail]
    budget_before: float
    budget_after: float
    total_points_hit: int
    free_transfers_before: int
    free_transfers_after: int
    transfer_errors: list[TransferError]
    squad_errors: list[SquadError]

    @property
    def is_valid(self) -> bool:
        return not self.transfer_errors and not self.squad_errors


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_players_with_teams(
    db: Session, player_ids: set[int], season_id: int
) -> dict[int, tuple[Player, Team]]:
    """Fetch Players+Teams for the given IDs in this season."""
    rows = db.execute(
        select(Player, Team)
        .join(Team, Team.id == Player.team_id)
        .where(Player.id.in_(player_ids), Player.season_id == season_id)
    ).all()
    return {p.id: (p, t) for p, t in rows}


def _get_active_squad_players(db: Session, squad_id: int) -> list[SquadPlayer]:
    return list(
        db.execute(
            select(SquadPlayer)
            .where(SquadPlayer.squad_id == squad_id, SquadPlayer.is_active.is_(True))
        ).scalars()
    )


def _delete_lineup_for_gw(db: Session, squad_id: int, gameweek_id: int) -> None:
    """Delete lineup snapshot so it rebuilds after transfer."""
    lineup = db.execute(
        select(GameweekLineup).where(
            GameweekLineup.squad_id == squad_id,
            GameweekLineup.gameweek_id == gameweek_id,
        )
    ).scalar_one_or_none()
    if not lineup:
        return
    for lp in db.execute(
        select(GameweekLineupPlayer).where(GameweekLineupPlayer.lineup_id == lineup.id)
    ).scalars():
        db.delete(lp)
    db.delete(lineup)


def _to_brief(player: Player, team: Team) -> PlayerBrief:
    return PlayerBrief(
        id=player.id,
        name=player.name,
        display_name=player.display_name,
        position=player.position.value,
        team_name=team.name,
        team_short_name=team.short_name,
        current_price=float(player.current_price),
    )


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_transfers_for_squad_gw(
    db: Session, squad_id: int, gameweek_id: int
) -> list[Transfer]:
    return list(
        db.execute(
            select(Transfer)
            .where(Transfer.squad_id == squad_id, Transfer.gameweek_id == gameweek_id)
            .order_by(Transfer.created_at)
        ).scalars()
    )


def get_transfer_history(
    db: Session, squad_id: int, *, page: int = 1, per_page: int = 20
) -> tuple[list[Transfer], int]:
    from sqlalchemy import func as sqlfunc
    base = select(Transfer).where(Transfer.squad_id == squad_id)
    total = db.execute(select(sqlfunc.count()).select_from(base.subquery())).scalar_one()
    rows = list(
        db.execute(
            base.order_by(Transfer.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        ).scalars()
    )
    return rows, total


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

def preview_transfers(
    db: Session,
    *,
    squad: Squad,
    gameweek: Gameweek,
    season_id: int,
    pairs: list[tuple[int, int]],
) -> TransferPreviewResult:
    """
    Compute what would happen if these transfers were applied.
    Does NOT write to DB.

    pairs: list of (player_out_id, player_in_id).
    """
    active_sps = _get_active_squad_players(db, squad.id)
    active_ids = {sp.player_id for sp in active_sps}

    # Pre-DB validation
    transfer_errors = validate_transfer_pairs(pairs, active_ids)
    if transfer_errors:
        return TransferPreviewResult(
            pairs=[],
            budget_before=float(squad.budget_remaining),
            budget_after=float(squad.budget_remaining),
            total_points_hit=0,
            free_transfers_before=squad.free_transfers_banked,
            free_transfers_after=squad.free_transfers_banked,
            transfer_errors=transfer_errors,
            squad_errors=[],
        )

    out_ids = {p[0] for p in pairs}
    in_ids = {p[1] for p in pairs}
    all_ids = out_ids | in_ids

    data = _fetch_players_with_teams(db, all_ids, season_id)

    # Check all IDs were found
    missing = all_ids - set(data.keys())
    if missing:
        return TransferPreviewResult(
            pairs=[],
            budget_before=float(squad.budget_remaining),
            budget_after=float(squad.budget_remaining),
            total_points_hit=0,
            free_transfers_before=squad.free_transfers_banked,
            free_transfers_after=squad.free_transfers_banked,
            transfer_errors=[TransferError("player_not_found", f"Players not found: {sorted(missing)}.")],
            squad_errors=[],
        )

    # Calculate projected squad
    projected_ids = (active_ids - out_ids) | in_ids

    # Fetch full projected squad for validation
    existing_players_data = _fetch_players_with_teams(db, active_ids - out_ids, season_id)
    all_projected: dict[int, tuple[Player, Team]] = {**existing_players_data, **{pid: data[pid] for pid in in_ids}}
    projected_players = [p for p, _ in all_projected.values()]
    projected_teams = {t.id: t for _, t in all_projected.values()}

    squad_errors = validate_squad(projected_players, projected_teams)

    # Budget calculation
    budget_before = float(squad.budget_remaining)
    budget_delta = sum(
        float(data[out_id][0].current_price) - float(data[in_id][0].current_price)
        for out_id, in_id in pairs
    )
    budget_after = round(budget_before + budget_delta, 1)

    # Points hit
    total_points_hit, paid_count = compute_points_hit(len(pairs), squad.free_transfers_banked)

    # Build pair details
    pair_details: list[TransferPairDetail] = []
    free_used = min(len(pairs), squad.free_transfers_banked)
    for i, (out_id, in_id) in enumerate(pairs):
        out_player, out_team = data[out_id]
        in_player, in_team = data[in_id]
        is_free = i < free_used
        pair_details.append(TransferPairDetail(
            player_out=_to_brief(out_player, out_team),
            player_in=_to_brief(in_player, in_team),
            price_out=float(out_player.current_price),
            price_in=float(in_player.current_price),
            is_free=is_free,
            point_cost=0 if is_free else POINTS_PER_EXTRA_TRANSFER,
        ))

    free_after = squad.free_transfers_banked - free_used

    return TransferPreviewResult(
        pairs=pair_details,
        budget_before=budget_before,
        budget_after=budget_after,
        total_points_hit=total_points_hit,
        free_transfers_before=squad.free_transfers_banked,
        free_transfers_after=free_after,
        transfer_errors=[],
        squad_errors=squad_errors,
    )


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def apply_transfers(
    db: Session,
    *,
    squad: Squad,
    gameweek: Gameweek,
    season_id: int,
    pairs: list[tuple[int, int]],
) -> tuple[list[Transfer], TransferPreviewResult]:
    """
    Atomically apply a batch of transfers.

    Returns (transfer_records, preview) — preview has is_valid=True if successful.
    If preview.is_valid is False, nothing is written.

    On success:
    - Soft-deletes outgoing SquadPlayers
    - Inserts incoming SquadPlayers with current purchase price
    - Creates Transfer records
    - Updates squad.budget_remaining and squad.free_transfers_banked
    - Deletes current GW lineup snapshot (rebuilt on next GET /lineups/current)
    """
    # Re-validate (defense against stale previews)
    preview = preview_transfers(
        db,
        squad=squad,
        gameweek=gameweek,
        season_id=season_id,
        pairs=pairs,
    )
    if not preview.is_valid:
        return [], preview

    active_sps = _get_active_squad_players(db, squad.id)
    active_sp_by_player = {sp.player_id: sp for sp in active_sps}

    out_ids = {p[0] for p in pairs}
    in_ids = {p[1] for p in pairs}
    all_ids = out_ids | in_ids
    data = _fetch_players_with_teams(db, all_ids, season_id)

    total_points_hit, paid_count = compute_points_hit(len(pairs), squad.free_transfers_banked)
    free_used = min(len(pairs), squad.free_transfers_banked)

    transfer_records: list[Transfer] = []

    for i, (out_id, in_id) in enumerate(pairs):
        out_player, _ = data[out_id]
        in_player, _ = data[in_id]
        is_free = i < free_used
        point_cost = 0 if is_free else POINTS_PER_EXTRA_TRANSFER

        # Soft-delete outgoing player
        sp_out = active_sp_by_player[out_id]
        sp_out.is_active = False
        sp_out.left_gameweek_id = gameweek.id

        # Insert incoming player
        sp_in = SquadPlayer(
            squad_id=squad.id,
            player_id=in_id,
            purchase_price=float(in_player.current_price),
            joined_gameweek_id=gameweek.id,
            is_active=True,
        )
        db.add(sp_in)

        # Transfer record
        record = Transfer(
            squad_id=squad.id,
            gameweek_id=gameweek.id,
            player_in_id=in_id,
            player_out_id=out_id,
            price_in=float(in_player.current_price),
            price_out=float(out_player.current_price),
            is_free=is_free,
            point_cost=point_cost,
        )
        db.add(record)
        transfer_records.append(record)

    # Update squad financials and free transfers
    squad.budget_remaining = round(preview.budget_after, 1)
    squad.free_transfers_banked = max(0, squad.free_transfers_banked - free_used)

    # Invalidate lineup snapshot
    _delete_lineup_for_gw(db, squad.id, gameweek.id)

    db.commit()
    for r in transfer_records:
        db.refresh(r)
    db.refresh(squad)

    return transfer_records, preview


# ---------------------------------------------------------------------------
# Free transfer rollover (called once per GW, e.g. via CLI script)
# ---------------------------------------------------------------------------

def rollover_free_transfers(db: Session, squad: Squad) -> int:
    """
    Credit free transfers for the new gameweek.

    Called after each GW deadline. Returns the new banked count.
    new_banked = min(current + FREE_TRANSFERS_PER_GW, MAX_FREE_TRANSFERS_BANKED)
    """
    from services.transfers.constants import FREE_TRANSFERS_PER_GW
    new_count = min(
        squad.free_transfers_banked + FREE_TRANSFERS_PER_GW,
        MAX_FREE_TRANSFERS_BANKED,
    )
    squad.free_transfers_banked = new_count
    db.commit()
    return new_count
