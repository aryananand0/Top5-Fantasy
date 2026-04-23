"""
Lineup service — DB operations for gameweek lineup management.

Snapshot model (MVP decision):
  - A lineup is created lazily on first GET for the current gameweek.
  - It snapshots the squad's 11 active players at creation time.
  - If the user replaces their squad before lock (PUT /squad), the current GW lineup
    is deleted so the next GET creates a fresh snapshot from the new squad.
  - After lock (is_locked=True), the lineup is frozen — no further edits.
  - The lock bit is synced to the gameweek status on every read.

This gives deterministic, easy-to-reason-about behaviour:
  squad replace → lineup reset → fresh snapshot on next fetch.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import GameweekStatus
from models.gameweek import Gameweek
from models.lineup import GameweekLineup, GameweekLineupPlayer
from models.player import Player
from models.squad import Squad, SquadPlayer
from models.team import Team
from services.lineups.validation import LineupError, validate_captain_selection

UTC = timezone.utc

# Statuses that mean the lineup can no longer be edited
_LOCKED_STATUSES = {
    GameweekStatus.LOCKED,
    GameweekStatus.ACTIVE,
    GameweekStatus.SCORING,
    GameweekStatus.FINISHED,
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class EnrichedLineupPlayer:
    lineup_player: GameweekLineupPlayer
    player: Player
    team: Team


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_lineup_for_squad_gw(
    db: Session,
    squad_id: int,
    gameweek_id: int,
) -> Optional[GameweekLineup]:
    return db.execute(
        select(GameweekLineup).where(
            GameweekLineup.squad_id == squad_id,
            GameweekLineup.gameweek_id == gameweek_id,
        )
    ).scalar_one_or_none()


def get_lineup_players(
    db: Session,
    lineup_id: int,
) -> list[EnrichedLineupPlayer]:
    """Return the 11 lineup players enriched with Player + Team data."""
    rows = db.execute(
        select(GameweekLineupPlayer, Player, Team)
        .join(Player, Player.id == GameweekLineupPlayer.player_id)
        .join(Team, Team.id == Player.team_id)
        .where(GameweekLineupPlayer.lineup_id == lineup_id)
        .order_by(Player.position, Player.name)
    ).all()
    return [
        EnrichedLineupPlayer(lineup_player=lp, player=p, team=t)
        for lp, p, t in rows
    ]


# ---------------------------------------------------------------------------
# Lineup lifecycle
# ---------------------------------------------------------------------------

def get_or_create_lineup(
    db: Session,
    *,
    squad: Squad,
    gameweek: Gameweek,
) -> GameweekLineup:
    """
    Return the existing lineup for this squad+gameweek, or create one now.

    Creation snapshots the squad's current 11 active players.
    Captain and vice-captain start as None — the user must set them before lock.
    """
    existing = get_lineup_for_squad_gw(db, squad.id, gameweek.id)
    if existing:
        return existing

    # Snapshot: fetch active squad players (ordered for determinism)
    squad_players = list(
        db.execute(
            select(SquadPlayer)
            .where(
                SquadPlayer.squad_id == squad.id,
                SquadPlayer.is_active.is_(True),
            )
            .order_by(SquadPlayer.id)
        ).scalars()
    )

    lineup = GameweekLineup(
        squad_id=squad.id,
        gameweek_id=gameweek.id,
        is_locked=False,
    )
    db.add(lineup)
    db.flush()  # get lineup.id

    for sp in squad_players:
        db.add(GameweekLineupPlayer(
            lineup_id=lineup.id,
            player_id=sp.player_id,
        ))

    db.commit()
    db.refresh(lineup)
    return lineup


def sync_lock_state(
    db: Session,
    lineup: GameweekLineup,
    gameweek: Gameweek,
) -> GameweekLineup:
    """
    Ensure lineup.is_locked reflects the current gameweek status.
    Called on every read so the lock bit stays accurate without a background job.
    """
    should_be_locked = gameweek.status in _LOCKED_STATUSES
    if should_be_locked and not lineup.is_locked:
        lineup.is_locked = True
        lineup.locked_at = datetime.now(UTC)
        db.commit()
        db.refresh(lineup)
    return lineup


def update_captain(
    db: Session,
    *,
    lineup: GameweekLineup,
    captain_player_id: int,
    vice_captain_player_id: int,
    lineup_player_ids: set[int],
) -> tuple[GameweekLineup, list[LineupError]]:
    """
    Set captain and vice-captain on the lineup.

    Returns (updated_lineup, []) on success or (lineup, errors) on failure.
    Callers must check errors before using the returned lineup.
    """
    errors = validate_captain_selection(
        captain_player_id,
        vice_captain_player_id,
        lineup_player_ids,
    )
    if errors:
        return lineup, errors

    lineup.captain_player_id = captain_player_id
    lineup.vice_captain_player_id = vice_captain_player_id
    db.commit()
    db.refresh(lineup)
    return lineup, []


def delete_lineup_for_squad_gw(
    db: Session,
    *,
    squad_id: int,
    gameweek_id: int,
) -> None:
    """
    Delete the lineup snapshot for this squad+gameweek.

    Called when the user replaces their squad (PUT /squad) before lock.
    The next GET /lineups/current will create a fresh snapshot from the new squad.
    No-op if no lineup exists.
    """
    lineup = get_lineup_for_squad_gw(db, squad_id, gameweek_id)
    if not lineup:
        return

    # Delete the lineup players first (no cascade on the FK)
    db.execute(
        select(GameweekLineupPlayer).where(
            GameweekLineupPlayer.lineup_id == lineup.id
        )
    )
    players = list(
        db.execute(
            select(GameweekLineupPlayer).where(
                GameweekLineupPlayer.lineup_id == lineup.id
            )
        ).scalars()
    )
    for lp in players:
        db.delete(lp)
    db.delete(lineup)
    db.commit()


def gameweek_is_editable(gameweek: Gameweek) -> bool:
    """Return True if lineup edits are still allowed for this gameweek."""
    return gameweek.status not in _LOCKED_STATUSES
