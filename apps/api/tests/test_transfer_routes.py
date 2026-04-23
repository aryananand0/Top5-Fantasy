"""
Transfer route tests — patched service layer, no real DB.

Follows the same pattern as test_lineup_routes.py:
  - service functions patched at route module import level
  - _get_current_user overridden to return a mock user
  - mock_db from conftest wired to the DB dependency
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from core.dependencies import _get_current_user
from main import app
from models.enums import GameweekStatus, Position
from tests.conftest import make_mock_user

SUMMARY_URL = "/api/v1/transfers/summary"
PREVIEW_URL = "/api/v1/transfers/preview"
APPLY_URL = "/api/v1/transfers/apply"
HISTORY_URL = "/api/v1/transfers/history"


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
    gw.status = status
    gw.is_current = True
    return gw


def _make_squad(free_transfers: int = 2, budget: float = 10.0) -> MagicMock:
    s = MagicMock()
    s.id = 42
    s.user_id = 99
    s.season_id = 1
    s.name = "Test FC"
    s.free_transfers_banked = free_transfers
    s.budget_remaining = budget
    s.total_points = 0
    s.overall_rank = None
    s.created_at = datetime(2025, 9, 1)
    s.updated_at = datetime(2025, 9, 1)
    return s


def _make_transfer(
    player_out_id: int = 1,
    player_in_id: int = 11,
    point_cost: int = 0,
    is_free: bool = True,
) -> MagicMock:
    t = MagicMock()
    t.id = 100
    t.squad_id = 42
    t.gameweek_id = 7
    t.player_out_id = player_out_id
    t.player_in_id = player_in_id
    t.price_out = 6.0
    t.price_in = 6.0
    t.is_free = is_free
    t.point_cost = point_cost
    t.created_at = datetime(2025, 10, 2, 10, 0, 0)
    return t


def _make_player_brief(pid: int = 1) -> MagicMock:
    p = MagicMock()
    p.id = pid
    p.name = f"Player {pid}"
    p.display_name = None
    p.position = "MID"
    p.team_name = "Team A"
    p.team_short_name = "TEA"
    p.current_price = 6.0
    return p


def _make_pair_detail(out_id: int = 1, in_id: int = 11, is_free: bool = True) -> MagicMock:
    pair = MagicMock()
    pair.player_out = _make_player_brief(out_id)
    pair.player_in = _make_player_brief(in_id)
    pair.price_out = 6.0
    pair.price_in = 6.0
    pair.is_free = is_free
    pair.point_cost = 0 if is_free else 4
    return pair


def _make_preview_result(
    is_valid: bool = True,
    transfer_errors=None,
    squad_errors=None,
    pairs=None,
) -> MagicMock:
    r = MagicMock()
    r.is_valid = is_valid
    r.transfer_errors = transfer_errors or []
    r.squad_errors = squad_errors or []
    r.pairs = pairs or [_make_pair_detail()]
    r.budget_before = 10.0
    r.budget_after = 10.0
    r.total_points_hit = 0
    r.free_transfers_before = 2
    r.free_transfers_after = 1
    return r


def _make_squad_detail(squad: MagicMock) -> MagicMock:
    detail = MagicMock()
    detail.squad = squad
    detail.total_cost = 90.0
    detail.members = []
    return detail


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def authed_client(client: TestClient):
    mock_user = make_mock_user(id=99, username="testuser", display_name="Test Manager")
    app.dependency_overrides[_get_current_user] = lambda: mock_user
    return client, mock_user


# ---------------------------------------------------------------------------
# GET /transfers/summary
# ---------------------------------------------------------------------------

class TestGetTransferSummary:
    def test_returns_summary(self, authed_client):
        client, _ = authed_client
        squad = _make_squad(free_transfers=2)
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=squad),
            patch("api.v1.routes.transfer.get_transfers_for_squad_gw", return_value=[]),
        ):
            resp = client.get(SUMMARY_URL, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["gameweek_number"] == 7
        assert body["free_transfers_available"] == 2
        assert body["transfers_made_this_gw"] == 0
        assert body["is_editable"] is True

    def test_is_not_editable_when_locked(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek(GameweekStatus.LOCKED)),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.transfer.get_transfers_for_squad_gw", return_value=[]),
        ):
            resp = client.get(SUMMARY_URL, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        assert resp.json()["is_editable"] is False

    def test_503_no_season(self, authed_client):
        client, _ = authed_client
        with patch("api.v1.routes.transfer.get_active_season", return_value=None):
            resp = client.get(SUMMARY_URL, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 503

    def test_404_no_squad(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=None),
        ):
            resp = client.get(SUMMARY_URL, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 404

    def test_401_unauthenticated(self, client: TestClient):
        resp = client.get(SUMMARY_URL)
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /transfers/preview
# ---------------------------------------------------------------------------

class TestPreviewTransfer:
    def _body(self, out_id: int = 1, in_id: int = 11):
        return {"transfers": [{"player_out_id": out_id, "player_in_id": in_id}]}

    def test_valid_preview_returns_200(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.transfer.preview_transfers", return_value=_make_preview_result()),
        ):
            resp = client.post(PREVIEW_URL, json=self._body(), headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_valid"] is True
        assert body["errors"] == []
        assert len(body["transfers"]) == 1

    def test_preview_with_errors_still_200(self, authed_client):
        client, _ = authed_client
        from services.transfers.validation import TransferError
        err_result = _make_preview_result(
            is_valid=False,
            transfer_errors=[TransferError("player_out_not_in_squad", "Player 1 is not in your squad.")],
            pairs=[],
        )
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.transfer.preview_transfers", return_value=err_result),
        ):
            resp = client.post(PREVIEW_URL, json=self._body(), headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_valid"] is False
        assert len(body["errors"]) == 1

    def test_preview_locked_gw_returns_200_not_editable(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek(GameweekStatus.LOCKED)),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
        ):
            resp = client.post(PREVIEW_URL, json=self._body(), headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_editable"] is False
        assert body["is_valid"] is False

    def test_422_missing_transfers_field(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
        ):
            resp = client.post(PREVIEW_URL, json={}, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 422

    def test_401_unauthenticated(self, client: TestClient):
        resp = client.post(PREVIEW_URL, json=self._body())
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /transfers/apply
# ---------------------------------------------------------------------------

class TestApplyTransfer:
    def _body(self, out_id: int = 1, in_id: int = 11):
        return {"transfers": [{"player_out_id": out_id, "player_in_id": in_id}]}

    def test_apply_success(self, authed_client):
        client, _ = authed_client
        squad = _make_squad(free_transfers=1)
        preview = _make_preview_result()
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=squad),
            patch("api.v1.routes.transfer.apply_transfers", return_value=([_make_transfer()], preview)),
            patch("api.v1.routes.transfer.get_transfers_for_squad_gw", return_value=[_make_transfer()]),
            patch("api.v1.routes.transfer.get_squad_detail", return_value=_make_squad_detail(squad)),
        ):
            resp = client.post(APPLY_URL, json=self._body(), headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert "squad" in body
        assert "applied_transfers" in body
        assert len(body["applied_transfers"]) == 1

    def test_apply_locked_gw_returns_403(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek(GameweekStatus.LOCKED)),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
        ):
            resp = client.post(APPLY_URL, json=self._body(), headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 403

    def test_apply_validation_fail_returns_400(self, authed_client):
        client, _ = authed_client
        from services.transfers.validation import TransferError
        invalid_preview = _make_preview_result(
            is_valid=False,
            transfer_errors=[TransferError("player_out_not_in_squad", "Player not in squad.")],
            pairs=[],
        )
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
            patch("api.v1.routes.transfer.apply_transfers", return_value=([], invalid_preview)),
        ):
            resp = client.post(APPLY_URL, json=self._body(), headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 400
        assert "errors" in resp.json()["detail"]

    def test_403_active_gw_also_blocked(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_current_gameweek", return_value=_make_gameweek(GameweekStatus.ACTIVE)),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=_make_squad()),
        ):
            resp = client.post(APPLY_URL, json=self._body(), headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 403

    def test_401_unauthenticated(self, client: TestClient):
        resp = client.post(APPLY_URL, json=self._body())
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /transfers/history
# ---------------------------------------------------------------------------

class TestGetTransferHistory:
    def test_returns_history_route_registered(self, authed_client):
        """Confirm the /history route is registered and auth is enforced."""
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=None),
        ):
            resp = client.get(HISTORY_URL, headers={"Authorization": "Bearer tok"})
        # No squad → empty response
        assert resp.status_code == 200
        assert resp.json()["transfers"] == []

    def test_empty_history_when_no_squad(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=None),
        ):
            resp = client.get(HISTORY_URL, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["transfers"] == []
        assert body["total"] == 0

    def test_503_no_season(self, authed_client):
        client, _ = authed_client
        with patch("api.v1.routes.transfer.get_active_season", return_value=None):
            resp = client.get(HISTORY_URL, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 503

    def test_401_unauthenticated(self, client: TestClient):
        resp = client.get(HISTORY_URL)
        assert resp.status_code == 401

    def test_pagination_params(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.transfer.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.transfer.get_squad_for_user", return_value=None),
        ):
            resp = client.get(
                HISTORY_URL + "?page=2&per_page=10",
                headers={"Authorization": "Bearer tok"},
            )
        assert resp.status_code == 200
