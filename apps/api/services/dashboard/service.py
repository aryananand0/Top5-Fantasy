"""
Dashboard aggregation service.

Assembles the full DashboardSummary in one pass for an authenticated user.
All data comes from existing tables — no new writes, pure read aggregation.

Query strategy: fetch each resource independently (simple indexed lookups).
No complex joins; readability wins over micro-optimisation at MVP scale.
"""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.enums import FixtureStatus, GameweekStatus
from models.fixture import Fixture
from models.gameweek import Gameweek
from models.lineup import GameweekLineup, GameweekLineupPlayer
from models.player import Player
from models.scoring import UserGameweekScore
from models.squad import Squad, SquadPlayer
from models.team import Team
from models.transfer import Transfer
from models.user import User
from schemas.dashboard import CaptainInfo, DashboardSummary, FixtureInfo

log = logging.getLogger(__name__)

# Gameweek statuses in which lineup / captain edits are still allowed
_EDITABLE_GW_STATUSES = {GameweekStatus.UPCOMING}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def get_dashboard_summary(db: Session, user: User) -> DashboardSummary:
    """
    Return a fully-assembled DashboardSummary for the authenticated user.

    Handles every "not ready" state gracefully:
      - No current gameweek  → gameweek fields are None
      - No squad             → squad/lineup/transfer fields are defaults
      - No lineup            → captain/VC are None
      - No GW score yet      → gw_points is None
    """
    gw = db.execute(
        select(Gameweek).where(Gameweek.is_current.is_(True))
    ).scalar_one_or_none()

    # Season total is user-scoped regardless of GW
    season_points: int = db.execute(
        select(func.coalesce(func.sum(UserGameweekScore.points), 0)).where(
            UserGameweekScore.user_id == user.id
        )
    ).scalar() or 0

    if gw is None:
        return _no_gameweek_response(season_points)

    squad = db.execute(
        select(Squad).where(Squad.user_id == user.id)
    ).scalar_one_or_none()

    if squad is None:
        return _no_squad_response(gw, season_points, db)

    return _full_response(db, user, gw, squad, season_points)


# ---------------------------------------------------------------------------
# Internal builders
# ---------------------------------------------------------------------------

def _no_gameweek_response(season_points: int) -> DashboardSummary:
    return DashboardSummary(
        gameweek_id=None, gameweek_number=None, gameweek_name=None,
        gameweek_status=None, deadline_at=None,
        gw_points=None, gw_raw_points=None,
        gw_transfer_cost=0, gw_captain_bonus=0,
        gw_rank=None, score_is_final=False,
        season_points=season_points,
        captain=None, vice_captain=None,
        has_squad=False, has_lineup=False,
        is_editable=False, can_transfer=False,
        free_transfers=0, transfers_made=0, transfer_hit=0,
        budget_remaining=0.0, fixtures=[],
    )


def _no_squad_response(gw: Gameweek, season_points: int, db: Session) -> DashboardSummary:
    fixtures = _get_fixtures(db, gw.id, squad_team_ids=set())
    return DashboardSummary(
        gameweek_id=gw.id,
        gameweek_number=gw.number,
        gameweek_name=gw.name or f"Gameweek {gw.number}",
        gameweek_status=gw.status.value,
        deadline_at=gw.deadline_at.isoformat(),
        gw_points=None, gw_raw_points=None,
        gw_transfer_cost=0, gw_captain_bonus=0,
        gw_rank=None, score_is_final=gw.status == GameweekStatus.FINISHED,
        season_points=season_points,
        captain=None, vice_captain=None,
        has_squad=False, has_lineup=False,
        is_editable=False, can_transfer=False,
        free_transfers=0, transfers_made=0, transfer_hit=0,
        budget_remaining=0.0, fixtures=fixtures,
    )


def _full_response(
    db: Session,
    user: User,
    gw: Gameweek,
    squad: Squad,
    season_points: int,
) -> DashboardSummary:
    # Squad players' team IDs for fixture highlighting
    squad_team_ids: set[int] = set(
        db.execute(
            select(Player.team_id)
            .join(SquadPlayer, Player.id == SquadPlayer.player_id)
            .where(SquadPlayer.squad_id == squad.id)
        ).scalars().all()
    )

    # Lineup snapshot for this GW
    lineup: Optional[GameweekLineup] = db.execute(
        select(GameweekLineup).where(
            GameweekLineup.squad_id == squad.id,
            GameweekLineup.gameweek_id == gw.id,
        )
    ).scalar_one_or_none()

    # GW user score (may not exist until scoring job runs)
    gw_score: Optional[UserGameweekScore] = db.execute(
        select(UserGameweekScore).where(
            UserGameweekScore.user_id == user.id,
            UserGameweekScore.gameweek_id == gw.id,
        )
    ).scalar_one_or_none()

    # Captain / VC info
    captain_info, vc_info = _build_captain_info(db, lineup)

    # Transfer counts for this GW
    transfer_rows = db.execute(
        select(Transfer.points_hit).where(
            Transfer.squad_id == squad.id,
            Transfer.gameweek_id == gw.id,
        )
    ).all()
    transfers_made = len(transfer_rows)
    transfer_hit = sum(row.points_hit for row in transfer_rows)

    # Editability flags
    is_editable = (
        gw.status in _EDITABLE_GW_STATUSES
        and (lineup is None or not lineup.is_locked)
    )
    can_transfer = gw.status == GameweekStatus.UPCOMING

    fixtures = _get_fixtures(db, gw.id, squad_team_ids=squad_team_ids)

    return DashboardSummary(
        gameweek_id=gw.id,
        gameweek_number=gw.number,
        gameweek_name=gw.name or f"Gameweek {gw.number}",
        gameweek_status=gw.status.value,
        deadline_at=gw.deadline_at.isoformat(),

        gw_points=gw_score.points if gw_score else None,
        gw_raw_points=(gw_score.points + gw_score.transfer_cost) if gw_score else None,
        gw_transfer_cost=gw_score.transfer_cost if gw_score else 0,
        gw_captain_bonus=gw_score.captain_points if gw_score else 0,
        gw_rank=gw_score.rank_global if gw_score else None,
        score_is_final=gw.status == GameweekStatus.FINISHED,

        season_points=season_points,
        captain=captain_info,
        vice_captain=vc_info,

        has_squad=True,
        has_lineup=lineup is not None,
        is_editable=is_editable,
        can_transfer=can_transfer,

        free_transfers=squad.free_transfers_banked,
        transfers_made=transfers_made,
        transfer_hit=transfer_hit,
        budget_remaining=float(squad.budget_remaining),

        fixtures=fixtures,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_captain_info(
    db: Session,
    lineup: Optional[GameweekLineup],
) -> tuple[Optional[CaptainInfo], Optional[CaptainInfo]]:
    """Load captain and VC player info, with per-player GW points if scored."""
    if lineup is None:
        return None, None

    # Per-player scored points (only populated after scoring job runs)
    player_gw_points: dict[int, Optional[int]] = {}
    if lineup.points_scored is not None:
        lp_rows = db.execute(
            select(GameweekLineupPlayer).where(
                GameweekLineupPlayer.lineup_id == lineup.id
            )
        ).scalars().all()
        player_gw_points = {lp.player_id: lp.points_scored for lp in lp_rows}

    def _make_info(player_id: Optional[int]) -> Optional[CaptainInfo]:
        if not player_id:
            return None
        player = db.get(Player, player_id)
        if not player:
            return None
        team = db.get(Team, player.team_id)
        return CaptainInfo(
            player_id=player.id,
            name=player.name,
            display_name=player.display_name,
            position=player.position.value,
            team_name=team.name if team else "",
            gw_points=player_gw_points.get(player_id),
        )

    return _make_info(lineup.captain_player_id), _make_info(lineup.vice_captain_player_id)


def _get_fixtures(
    db: Session,
    gameweek_id: int,
    squad_team_ids: set[int],
    limit: int = 5,
) -> list[FixtureInfo]:
    """
    Return up to `limit` fixtures for the gameweek, ordered by kickoff_at.
    Fixtures involving the user's squad players are marked has_squad_players=True.
    """
    fixtures = db.execute(
        select(Fixture)
        .where(Fixture.gameweek_id == gameweek_id)
        .order_by(Fixture.kickoff_at.asc().nulls_last())
        .limit(limit + 2)   # fetch a couple extra in case of postponed fixtures
    ).scalars().all()

    if not fixtures:
        return []

    # Batch load team names
    team_ids = {f.home_team_id for f in fixtures} | {f.away_team_id for f in fixtures}
    teams: dict[int, Team] = {
        t.id: t
        for t in db.execute(select(Team).where(Team.id.in_(team_ids))).scalars().all()
    }

    result: list[FixtureInfo] = []
    for f in fixtures:
        if f.status == FixtureStatus.CANCELLED:
            continue   # skip cancelled fixtures in the preview
        home = teams.get(f.home_team_id)
        away = teams.get(f.away_team_id)
        result.append(FixtureInfo(
            fixture_id=f.id,
            home_team=home.name if home else "Unknown",
            home_team_short=(home.short_name or home.name) if home else "",
            away_team=away.name if away else "Unknown",
            away_team_short=(away.short_name or away.name) if away else "",
            home_score=f.home_score,
            away_score=f.away_score,
            kickoff_at=f.kickoff_at.isoformat() if f.kickoff_at else None,
            status=f.status.value,
            has_squad_players=(
                f.home_team_id in squad_team_ids or f.away_team_id in squad_team_ids
            ),
        ))
        if len(result) == limit:
            break

    return result
