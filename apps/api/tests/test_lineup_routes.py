"""
Lineup route tests — patched service layer, no real DB.

Follows the same pattern as test_squad_routes.py:
  - service functions patched at route module import level
  - _get_current_user overridden to return a mock user
  - mock_db from conftest wired to the DB dependency
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from core.dependencies import _get_current_user
from main import app
from tests.conftest import make_mock_user
from models.enums import GameweekStatus, Position

LINEUP_URL = "/api/v1/lineups/current"


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

def _make_season() -> MagicMock:
    s = MagicMock()
    s.id = 1
    s.label = "2024-25"
    s.is_active = True
    return s


def _make_gameweek(status: GameweekStatus = GameweekStatus.UPCOMING) -> MagicMock:
    gw = MagicMock()
    gw.id = 7
    gw.number = 7
    gw.name = "Gameweek 7"
    gw.deadline_at = datetime(2025, 10, 3, 12, 0, 0)
    gw.start_at = datetime(2025, 10, 4, 12, 0, 0)
    gw.end_at = datetime(2025, 10, 9, 23, 59, 59)
    gw.status = status
    gw.is_current = True
    return gw


def _make_squad() -> MagicMock:
    s = MagicMock()
    s.id = 42
    s.user_id = 99
    s.season_id = 1
    s.name = "Test FC"
    return s


def _make_lineup(
    captain_player_id: int | None = None,
    vice_captain_player_id: int | None = None,
    is_locked: bool = False,
) -> MagicMock:
    lineup = MagicMock()
    lineup.id = 1
    lineup.squad_id = 42
    lineup.gameweek_id = 7
    lineup.captain_player_id = captain_player_id
    lineup.vice_captain_player_id = vice_captain_player_id
    lineup.is_locked = is_locked
    lineup.locked_at = None
    lineup.points_scored = None
    lineup.transfer_cost_applied = 0
    lineup.created_at = datetime(2025, 10, 1, 12, 0, 0)
    lineup.updated_at = datetime(2025, 10, 1, 12, 0, 0)
    return lineup


def _make_enriched_players(
    captain_id: int | None = None,
    vc_id: int | None = None,
) -> list[MagicMock]:
    """Build 11 mock EnrichedLineupPlayer objects."""
    players = []
    positions = [Position.GK] + [Position.DEF] * 3 + [Position.MID] * 4 + [Position.FWD] * 3
    for i, pos in enumerate(positions, start=1):
        ep = MagicMock()
        ep.player.id = i
        ep.player.name = f"Player {i}"
        ep.player.display_name = None
        ep.player.position = pos
        ep.player.current_price = 5.0
        ep.player.form_score = 0.0
        ep.player.is_available = True
        ep.team.name = f"Team {i}"
        ep.team.short_name = f"T{i}"
        ep.lineup_player.points_scored = None
        players.append(ep)
    return players


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def authed_client(client: TestClient) -> tuple[TestClient, MagicMock]:
    mock_user = make_mock_user(id=99, username="testuser", display_name="Test Manager")
    app.dependency_overrides[_get_current_user] = lambda: mock_user
    return client, mock_user


# ---------------------------------------------------------------------------
# GET /lineups/current
# ---------------------------------------------------------------------------

class TestGetCurrentLineup:
    def test_returns_lineup_when_exists(self, authed_client):
        client, _ = authed_client
        lineup = _make_lineup(captain_player_id=1, vice_captain_player_id=2)
        gw = _make_gameweek()
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=gw),
            patch("api.v1.routes.lineup.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.lineup.get_or_create_lineup", return_value=lineup),
            patch("api.v1.routes.lineup.sync_lock_state", return_value=lineup),
            patch("api.v1.routes.lineup.get_lineup_players", return_value=_make_enriched_players(1, 2)),
        ):
            resp = client.get(LINEUP_URL, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["gameweek_number"] == 7
        assert body["captain_player_id"] == 1
        assert body["vice_captain_player_id"] == 2
        assert len(body["players"]) == 11
        assert body["is_editable"] is True

    def test_is_editable_false_when_locked(self, authed_client):
        client, _ = authed_client
        lineup = _make_lineup(is_locked=True)
        gw = _make_gameweek(GameweekStatus.LOCKED)
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=gw),
            patch("api.v1.routes.lineup.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.lineup.get_or_create_lineup", return_value=lineup),
            patch("api.v1.routes.lineup.sync_lock_state", return_value=lineup),
            patch("api.v1.routes.lineup.get_lineup_players", return_value=_make_enriched_players()),
        ):
            resp = client.get(LINEUP_URL, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        assert resp.json()["is_editable"] is False
        assert resp.json()["is_locked"] is True

    def test_503_when_no_season(self, authed_client):
        client, _ = authed_client
        with patch("api.v1.routes.lineup.get_active_season", return_value=None):
            resp = client.get(LINEUP_URL, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 503

    def test_404_when_no_current_gw(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=None),
        ):
            resp = client.get(LINEUP_URL, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 404

    def test_404_when_no_squad(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.lineup.get_squad_for_user", return_value=None),
        ):
            resp = client.get(LINEUP_URL, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 404

    def test_401_without_auth(self, client: TestClient):
        resp = client.get(LINEUP_URL)
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# PUT /lineups/current
# ---------------------------------------------------------------------------

class TestUpdateCurrentLineup:
    VALID_PAYLOAD = {"captain_player_id": 1, "vice_captain_player_id": 2}

    def test_updates_captain_and_vc(self, authed_client):
        client, _ = authed_client
        lineup = _make_lineup(captain_player_id=1, vice_captain_player_id=2)
        gw = _make_gameweek()
        enriched = _make_enriched_players(1, 2)
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=gw),
            patch("api.v1.routes.lineup.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.lineup.get_or_create_lineup", return_value=lineup),
            patch("api.v1.routes.lineup.sync_lock_state", return_value=lineup),
            patch("api.v1.routes.lineup.get_lineup_players", return_value=enriched),
            patch("api.v1.routes.lineup.update_captain", return_value=(lineup, [])),
        ):
            resp = client.put(
                LINEUP_URL,
                json=self.VALID_PAYLOAD,
                headers={"Authorization": "Bearer tok"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["captain_player_id"] == 1
        assert body["vice_captain_player_id"] == 2

    def test_403_when_locked(self, authed_client):
        client, _ = authed_client
        locked_lineup = _make_lineup(is_locked=True)
        gw = _make_gameweek(GameweekStatus.LOCKED)
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=gw),
            patch("api.v1.routes.lineup.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.lineup.get_or_create_lineup", return_value=locked_lineup),
            patch("api.v1.routes.lineup.sync_lock_state", return_value=locked_lineup),
        ):
            resp = client.put(
                LINEUP_URL,
                json=self.VALID_PAYLOAD,
                headers={"Authorization": "Bearer tok"},
            )

        assert resp.status_code == 403
        assert "locked" in resp.json()["detail"].lower()

    def test_400_when_same_player_captain_and_vc(self, authed_client):
        from services.lineups.validation import LineupError
        client, _ = authed_client
        lineup = _make_lineup()
        gw = _make_gameweek()
        errors = [LineupError("same_player", "Captain and vice-captain must be different players.")]
        enriched = _make_enriched_players()
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=gw),
            patch("api.v1.routes.lineup.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.lineup.get_or_create_lineup", return_value=lineup),
            patch("api.v1.routes.lineup.sync_lock_state", return_value=lineup),
            patch("api.v1.routes.lineup.get_lineup_players", return_value=enriched),
            patch("api.v1.routes.lineup.update_captain", return_value=(lineup, errors)),
        ):
            resp = client.put(
                LINEUP_URL,
                json={"captain_player_id": 3, "vice_captain_player_id": 3},
                headers={"Authorization": "Bearer tok"},
            )

        assert resp.status_code == 400
        body = resp.json()
        assert "errors" in body["detail"]
        assert len(body["detail"]["errors"]) == 1

    def test_400_when_captain_not_in_lineup(self, authed_client):
        from services.lineups.validation import LineupError
        client, _ = authed_client
        lineup = _make_lineup()
        gw = _make_gameweek()
        errors = [LineupError("captain_not_in_lineup", "Captain must be one of your 11 lineup players.")]
        enriched = _make_enriched_players()
        with (
            patch("api.v1.routes.lineup.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.lineup.get_current_gameweek", return_value=gw),
            patch("api.v1.routes.lineup.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.lineup.get_or_create_lineup", return_value=lineup),
            patch("api.v1.routes.lineup.sync_lock_state", return_value=lineup),
            patch("api.v1.routes.lineup.get_lineup_players", return_value=enriched),
            patch("api.v1.routes.lineup.update_captain", return_value=(lineup, errors)),
        ):
            resp = client.put(
                LINEUP_URL,
                json={"captain_player_id": 999, "vice_captain_player_id": 2},
                headers={"Authorization": "Bearer tok"},
            )

        assert resp.status_code == 400

    def test_422_when_payload_missing_captain(self, authed_client):
        client, _ = authed_client
        resp = client.put(
            LINEUP_URL,
            json={"vice_captain_player_id": 2},
            headers={"Authorization": "Bearer tok"},
        )
        assert resp.status_code == 422

    def test_401_without_auth(self, client: TestClient):
        resp = client.put(LINEUP_URL, json={"captain_player_id": 1, "vice_captain_player_id": 2})
        assert resp.status_code in (401, 403)
