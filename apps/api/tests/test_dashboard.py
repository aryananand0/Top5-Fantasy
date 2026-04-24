"""
Dashboard service unit tests.

Uses mock DB sessions — no real PostgreSQL needed.
Tests the three response paths: no GW, no squad, full response.
"""

import os
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost/top5fantasy_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-used-in-prod")

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from models.enums import FixtureStatus, GameweekStatus, Position
from services.dashboard.service import (
    _build_captain_info,
    _get_fixtures,
    _no_gameweek_response,
    _no_squad_response,
)


UTC = timezone.utc
_DT = datetime(2025, 8, 10, 15, 0, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_db():
    return MagicMock()


def _gameweek(
    id=1,
    number=1,
    name="Gameweek 1",
    status=GameweekStatus.UPCOMING,
    deadline_at=_DT,
    is_current=True,
):
    gw = MagicMock()
    gw.id = id
    gw.number = number
    gw.name = name
    gw.status = status
    gw.deadline_at = deadline_at
    gw.is_current = is_current
    return gw


def _squad(id=1, user_id=1, free_transfers_banked=1, budget_remaining=Decimal("4.5")):
    s = MagicMock()
    s.id = id
    s.user_id = user_id
    s.free_transfers_banked = free_transfers_banked
    s.budget_remaining = budget_remaining
    return s


def _player(id=1, name="Test Player", display_name="T. Player", team_id=10, position=Position.MID):
    p = MagicMock()
    p.id = id
    p.name = name
    p.display_name = display_name
    p.team_id = team_id
    p.position = position
    return p


def _team(id=10, name="Test FC", short_name="TST"):
    t = MagicMock()
    t.id = id
    t.name = name
    t.short_name = short_name
    return t


def _fixture_obj(
    id=1,
    gameweek_id=1,
    home_team_id=10,
    away_team_id=20,
    home_score=None,
    away_score=None,
    kickoff_at=_DT,
    status=FixtureStatus.SCHEDULED,
):
    f = MagicMock()
    f.id = id
    f.gameweek_id = gameweek_id
    f.home_team_id = home_team_id
    f.away_team_id = away_team_id
    f.home_score = home_score
    f.away_score = away_score
    f.kickoff_at = kickoff_at
    f.status = status
    return f


def _lineup(
    id=1,
    squad_id=1,
    gameweek_id=1,
    captain_player_id=1,
    vice_captain_player_id=2,
    points_scored=None,
    is_locked=False,
):
    l = MagicMock()
    l.id = id
    l.squad_id = squad_id
    l.gameweek_id = gameweek_id
    l.captain_player_id = captain_player_id
    l.vice_captain_player_id = vice_captain_player_id
    l.points_scored = points_scored
    l.is_locked = is_locked
    return l


# ---------------------------------------------------------------------------
# _no_gameweek_response
# ---------------------------------------------------------------------------

def test_no_gameweek_response_defaults():
    summary = _no_gameweek_response(season_points=42)
    assert summary.gameweek_id is None
    assert summary.season_points == 42
    assert summary.has_squad is False
    assert summary.has_lineup is False
    assert summary.is_editable is False
    assert summary.fixtures == []
    assert summary.captain is None


# ---------------------------------------------------------------------------
# _no_squad_response
# ---------------------------------------------------------------------------

def test_no_squad_response():
    gw = _gameweek()
    db = _make_db()
    db.execute.return_value.scalars.return_value.all.return_value = []

    with patch("services.dashboard.service._get_fixtures", return_value=[]) as mock_fix:
        summary = _no_squad_response(gw, season_points=10, db=db)

    assert summary.gameweek_id == 1
    assert summary.gameweek_number == 1
    assert summary.has_squad is False
    assert summary.season_points == 10
    assert summary.captain is None


# ---------------------------------------------------------------------------
# _build_captain_info
# ---------------------------------------------------------------------------

def test_build_captain_info_no_lineup():
    db = _make_db()
    cap, vc = _build_captain_info(db, lineup=None)
    assert cap is None
    assert vc is None


def test_build_captain_info_unscored_lineup():
    """Lineup exists but scoring hasn't run — gw_points should be None."""
    lineup = _lineup(points_scored=None)
    player = _player(id=1)
    team = _team()

    db = _make_db()
    db.get.side_effect = lambda model, pid: (player if pid == 1 else _player(id=2)) if "Player" in str(model) else team

    cap, vc = _build_captain_info(db, lineup)
    assert cap is not None
    assert cap.player_id == 1
    assert cap.gw_points is None


def test_build_captain_info_scored_lineup():
    """After scoring runs — gw_points should be populated from lineup player row."""
    lineup = _lineup(points_scored=50)

    lp1 = MagicMock()
    lp1.player_id = 1
    lp1.points_scored = 12  # captain 2×

    lp2 = MagicMock()
    lp2.player_id = 2
    lp2.points_scored = 5

    player1 = _player(id=1)
    player2 = _player(id=2)
    team = _team()

    db = _make_db()
    # execute() call is for fetching lineup players
    db.execute.return_value.scalars.return_value.all.return_value = [lp1, lp2]
    db.get.side_effect = lambda model, pid: (player1 if pid == 1 else player2) if "Player" in str(model) else team

    cap, vc = _build_captain_info(db, lineup)
    assert cap.gw_points == 12
    assert vc.gw_points == 5


# ---------------------------------------------------------------------------
# _get_fixtures
# ---------------------------------------------------------------------------

def test_get_fixtures_empty():
    db = _make_db()
    db.execute.return_value.scalars.return_value.all.return_value = []
    result = _get_fixtures(db, gameweek_id=1, squad_team_ids=set())
    assert result == []


def test_get_fixtures_skips_cancelled():
    home = _team(id=10, name="Home FC", short_name="HOM")
    away = _team(id=20, name="Away United", short_name="AWY")

    f1 = _fixture_obj(id=1, home_team_id=10, away_team_id=20, status=FixtureStatus.CANCELLED)
    f2 = _fixture_obj(id=2, home_team_id=10, away_team_id=20, status=FixtureStatus.SCHEDULED)

    db = _make_db()
    # First execute: fixtures; second execute: teams
    db.execute.return_value.scalars.return_value.all.side_effect = [
        [f1, f2],
        [home, away],
    ]

    result = _get_fixtures(db, gameweek_id=1, squad_team_ids=set())
    assert len(result) == 1
    assert result[0].fixture_id == 2


def test_get_fixtures_has_squad_players_flag():
    home = _team(id=10, name="Home FC", short_name="HOM")
    away = _team(id=20, name="Away United", short_name="AWY")

    f = _fixture_obj(id=1, home_team_id=10, away_team_id=20, status=FixtureStatus.SCHEDULED)

    db = _make_db()
    db.execute.return_value.scalars.return_value.all.side_effect = [
        [f],
        [home, away],
    ]

    # User has a player in team 10
    result = _get_fixtures(db, gameweek_id=1, squad_team_ids={10})
    assert result[0].has_squad_players is True


def test_get_fixtures_limit():
    home = _team(id=10, name="Home FC", short_name="HOM")
    away = _team(id=20, name="Away United", short_name="AWY")

    fixtures = [
        _fixture_obj(id=i, home_team_id=10, away_team_id=20, status=FixtureStatus.SCHEDULED)
        for i in range(1, 9)
    ]

    db = _make_db()
    db.execute.return_value.scalars.return_value.all.side_effect = [
        fixtures,
        [home, away],
    ]

    result = _get_fixtures(db, gameweek_id=1, squad_team_ids=set(), limit=5)
    assert len(result) == 5


# ---------------------------------------------------------------------------
# Editability flags
# ---------------------------------------------------------------------------

def test_is_editable_when_upcoming_and_no_lineup():
    """Upcoming GW + no lineup → editable."""
    from services.dashboard.service import _full_response
    from models.enums import GameweekStatus

    gw = _gameweek(status=GameweekStatus.UPCOMING)
    squad = _squad()

    db = _make_db()
    # squad team IDs
    db.execute.return_value.scalars.return_value.all.return_value = []
    # lineup = None, gw_score = None, transfers = []
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.execute.return_value.all.return_value = []

    user = MagicMock()
    user.id = 1

    with (
        patch("services.dashboard.service._build_captain_info", return_value=(None, None)),
        patch("services.dashboard.service._get_fixtures", return_value=[]),
    ):
        summary = _full_response(db, user, gw, squad, season_points=0)

    assert summary.is_editable is True
    assert summary.can_transfer is True


def test_is_not_editable_when_finished():
    """Finished GW → not editable, not transferable."""
    from services.dashboard.service import _full_response

    gw = _gameweek(status=GameweekStatus.FINISHED)
    squad = _squad()

    db = _make_db()
    db.execute.return_value.scalars.return_value.all.return_value = []
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.execute.return_value.all.return_value = []

    user = MagicMock()
    user.id = 1

    with (
        patch("services.dashboard.service._build_captain_info", return_value=(None, None)),
        patch("services.dashboard.service._get_fixtures", return_value=[]),
    ):
        summary = _full_response(db, user, gw, squad, season_points=0)

    assert summary.is_editable is False
    assert summary.can_transfer is False
