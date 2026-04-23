"""
Squad service — DB operations for squad creation and retrieval.

Validation is deliberately separate (validation.py) so the same rules
can be reused for transfer previews in Step 13 without touching this file.

Squad lifecycle for MVP:
  - POST /squad creates a squad once per user per season
  - PUT  /squad replaces the squad freely until the first GW is LOCKED/ACTIVE
  - After that, changes go through the transfer system (Step 13)
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import GameweekStatus, Position
from models.gameweek import Gameweek
from models.player import Player
from models.season import Season
from models.squad import Squad, SquadPlayer
from models.team import Team
from services.squads.constants import (
    BUDGET_CAP,
    INITIAL_FREE_TRANSFERS,
    POSITION_REQUIREMENTS,
    SQUAD_SIZE,
)
from services.squads.validation import (
    SquadError,
    validate_player_ids,
    validate_squad,
)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class EnrichedSquadPlayer:
    """A squad player with joined Player + Team data, ready for serialisation."""
    squad_player: SquadPlayer
    player: Player
    team: Team


@dataclass
class SquadDetail:
    squad: Squad
    members: list[EnrichedSquadPlayer]

    @property
    def total_cost(self) -> float:
        return round(sum(float(m.squad_player.purchase_price) for m in self.members), 1)


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_squad_for_user(db: Session, user_id: int, season_id: int) -> Optional[Squad]:
    return db.execute(
        select(Squad).where(
            Squad.user_id == user_id,
            Squad.season_id == season_id,
        )
    ).scalar_one_or_none()


def get_squad_detail(db: Session, squad: Squad) -> SquadDetail:
    """Return a SquadDetail with all active players joined to Player + Team."""
    rows = db.execute(
        select(SquadPlayer, Player, Team)
        .join(Player, Player.id == SquadPlayer.player_id)
        .join(Team, Team.id == Player.team_id)
        .where(
            SquadPlayer.squad_id == squad.id,
            SquadPlayer.is_active.is_(True),
        )
        .order_by(Player.position, Player.name)
    ).all()

    members = [
        EnrichedSquadPlayer(squad_player=sp, player=p, team=t)
        for sp, p, t in rows
    ]
    return SquadDetail(squad=squad, members=members)


def get_active_season(db: Session) -> Optional[Season]:
    return db.execute(
        select(Season).where(Season.is_active.is_(True))
    ).scalar_one_or_none()


def season_is_locked(db: Session, season_id: int) -> bool:
    """
    Return True if any gameweek in the season is LOCKED, ACTIVE, SCORING, or FINISHED.
    Once locked, squad changes require the transfer system, not a full replace.
    """
    locked = db.execute(
        select(Gameweek).where(
            Gameweek.season_id == season_id,
            Gameweek.status.in_([
                GameweekStatus.LOCKED,
                GameweekStatus.ACTIVE,
                GameweekStatus.SCORING,
                GameweekStatus.FINISHED,
            ])
        ).limit(1)
    ).scalar_one_or_none()
    return locked is not None


# ---------------------------------------------------------------------------
# Fetch and validate helpers
# ---------------------------------------------------------------------------

def fetch_and_validate(
    db: Session,
    player_ids: list[int],
    season_id: int,
) -> tuple[list[Player], dict[int, Team], list[SquadError]]:
    """
    Fetch Players + Teams for the submitted IDs, run full validation.
    Returns (players, teams_by_team_id, errors).
    """
    # Pre-DB checks first (saves round trip on obvious mistakes)
    pre_errors = validate_player_ids(player_ids)
    if pre_errors:
        return [], {}, pre_errors

    # Fetch players — must exist and belong to this season
    players = list(
        db.execute(
            select(Player)
            .where(
                Player.id.in_(player_ids),
                Player.season_id == season_id,
            )
        ).scalars()
    )

    # Detect any IDs that don't exist or belong to a different season
    found_ids = {p.id for p in players}
    missing = set(player_ids) - found_ids
    if missing:
        return [], {}, [SquadError(
            "player_not_found",
            f"Player(s) not found in this season: {sorted(missing)}.",
        )]

    # Fetch all teams for the selected players
    team_ids = {p.team_id for p in players}
    teams_list = list(
        db.execute(select(Team).where(Team.id.in_(team_ids))).scalars()
    )
    teams = {t.id: t for t in teams_list}

    errors = validate_squad(players, teams)
    return players, teams, errors


# ---------------------------------------------------------------------------
# Squad mutations
# ---------------------------------------------------------------------------

def create_squad(
    db: Session,
    *,
    user_id: int,
    season_id: int,
    player_ids: list[int],
    squad_name: str,
) -> tuple[SquadDetail, list[SquadError]]:
    """
    Create a new squad for user/season.

    Returns (SquadDetail, []) on success, or (None-ish, errors) on failure.
    Callers should check that errors is empty before using the returned detail.
    """
    players, teams, errors = fetch_and_validate(db, player_ids, season_id)
    if errors:
        return _empty_detail(), errors

    total_cost = round(sum(float(p.current_price) for p in players), 1)
    budget_remaining = round(BUDGET_CAP - total_cost, 1)

    squad = Squad(
        user_id=user_id,
        season_id=season_id,
        name=squad_name,
        budget_remaining=budget_remaining,
        free_transfers_banked=INITIAL_FREE_TRANSFERS,
    )
    db.add(squad)
    db.flush()  # get squad.id without committing

    _insert_squad_players(db, squad.id, players)
    db.commit()
    db.refresh(squad)

    return get_squad_detail(db, squad), []


def replace_squad(
    db: Session,
    *,
    squad: Squad,
    player_ids: list[int],
    season_id: int,
) -> tuple[SquadDetail, list[SquadError]]:
    """
    Replace all active squad players with a new selection.
    Used by PUT /squad before the season locks.

    Old squad_players are soft-deleted (is_active=False) to preserve history.
    """
    players, teams, errors = fetch_and_validate(db, player_ids, season_id)
    if errors:
        return _empty_detail(), errors

    # Soft-delete current active players
    existing = list(
        db.execute(
            select(SquadPlayer).where(
                SquadPlayer.squad_id == squad.id,
                SquadPlayer.is_active.is_(True),
            )
        ).scalars()
    )
    for sp in existing:
        sp.is_active = False

    # Add new players
    _insert_squad_players(db, squad.id, players)

    # Update budget_remaining
    total_cost = round(sum(float(p.current_price) for p in players), 1)
    squad.budget_remaining = round(BUDGET_CAP - total_cost, 1)

    db.commit()
    db.refresh(squad)

    return get_squad_detail(db, squad), []


def _insert_squad_players(db: Session, squad_id: int, players: list[Player]) -> None:
    for player in players:
        db.add(SquadPlayer(
            squad_id=squad_id,
            player_id=player.id,
            purchase_price=float(player.current_price),
            is_active=True,
        ))


def _empty_detail() -> SquadDetail:
    """Sentinel return value when errors prevent squad creation."""
    return SquadDetail(squad=Squad(), members=[])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Player browsing (needed for squad builder UI)
# ---------------------------------------------------------------------------

def list_players(
    db: Session,
    season_id: int,
    *,
    position: Optional[Position] = None,
    team_id: Optional[int] = None,
    search: Optional[str] = None,
    available_only: bool = True,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[tuple[Player, Team]], int]:
    """
    Return paginated (Player, Team) pairs for the player browser.
    Also returns total count for pagination metadata.
    """
    stmt = (
        select(Player, Team)
        .join(Team, Team.id == Player.team_id)
        .where(Player.season_id == season_id)
    )

    if available_only:
        stmt = stmt.where(Player.is_available.is_(True))
    if position:
        stmt = stmt.where(Player.position == position)
    if team_id:
        stmt = stmt.where(Player.team_id == team_id)
    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            Player.name.ilike(term) | Player.display_name.ilike(term)
        )

    # Count total before pagination
    from sqlalchemy import func as sqlfunc
    count_stmt = select(sqlfunc.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # Apply ordering and pagination
    stmt = (
        stmt
        .order_by(Player.position, Player.current_price.desc(), Player.name)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    rows = list(db.execute(stmt).all())

    return rows, total
