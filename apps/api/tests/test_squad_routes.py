"""
Squad route tests — patched service layer, no real DB.

Follows the same pattern as test_auth.py:
  - service functions are patched at the route module's import level
  - _get_current_user is overridden to return a mock user
  - mock_db fixture from conftest is wired to the DB dependency
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from core.dependencies import _get_current_user
from main import app
from tests.conftest import make_mock_user

SQUAD_URL = "/api/v1/squad"


# ---------------------------------------------------------------------------
# Shared stubs
# ---------------------------------------------------------------------------

def _make_squad_detail(budget_remaining: float = 42.0) -> MagicMock:
    """Return a MagicMock shaped like a SquadDetail with 11 players."""
    squad = MagicMock()
    squad.id = 1
    squad.name = "Test FC"
    squad.budget_remaining = budget_remaining
    squad.total_points = 0
    squad.overall_rank = None
    squad.free_transfers_banked = 1
    squad.created_at = datetime(2025, 8, 1, 12, 0, 0)
    squad.updated_at = datetime(2025, 8, 1, 12, 0, 0)

    # Build 11 mock members
    members = []
    from models.enums import Position
    positions = [Position.GK] + [Position.DEF] * 3 + [Position.MID] * 4 + [Position.FWD] * 3
    for i, pos in enumerate(positions, start=1):
        m = MagicMock()
        m.player.id = i
        m.player.name = f"Player {i}"
        m.player.display_name = None
        m.player.position = pos
        m.player.form_score = 0.0
        m.player.starter_confidence = 3
        m.player.is_available = True
        m.player.current_price = 5.0
        m.team.id = i
        m.team.name = f"Team {i}"
        m.squad_player.purchase_price = 5.0
        members.append(m)

    detail = MagicMock()
    detail.squad = squad
    detail.members = members
    detail.total_cost = round(100.0 - budget_remaining, 1)
    return detail


def _make_season() -> MagicMock:
    season = MagicMock()
    season.id = 1
    season.label = "2024-25"
    season.is_active = True
    return season


VALID_PAYLOAD = {"player_ids": list(range(1, 12))}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def authed_client(client: TestClient) -> tuple[TestClient, MagicMock]:
    """TestClient with auth dependency pre-overridden."""
    mock_user = make_mock_user(id=99, username="testmanager", display_name="Test Manager")
    app.dependency_overrides[_get_current_user] = lambda: mock_user
    return client, mock_user


# ---------------------------------------------------------------------------
# GET /squad
# ---------------------------------------------------------------------------

class TestGetSquad:
    def test_returns_squad_when_exists(self, authed_client):
        client, _ = authed_client
        detail = _make_squad_detail()
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=MagicMock()),
            patch("api.v1.routes.squad.get_squad_detail", return_value=detail),
        ):
            resp = client.get(SQUAD_URL, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == 1
        assert body["name"] == "Test FC"
        assert len(body["players"]) == 11

    def test_404_when_no_squad(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=None),
        ):
            resp = client.get(SQUAD_URL, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 404

    def test_503_when_no_active_season(self, authed_client):
        client, _ = authed_client
        with patch("api.v1.routes.squad.get_active_season", return_value=None):
            resp = client.get(SQUAD_URL, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 503

    def test_401_without_auth(self, client: TestClient):
        resp = client.get(SQUAD_URL)
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# POST /squad
# ---------------------------------------------------------------------------

class TestCreateSquad:
    def test_creates_squad_successfully(self, authed_client):
        client, user = authed_client
        detail = _make_squad_detail()
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=None),
            patch("api.v1.routes.squad.create_squad", return_value=(detail, [])),
        ):
            resp = client.post(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == 1
        assert len(body["players"]) == 11

    def test_uses_display_name_for_default_squad_name(self, authed_client):
        client, user = authed_client
        detail = _make_squad_detail()
        captured_args = {}

        def mock_create(db, *, user_id, season_id, player_ids, squad_name):
            captured_args["squad_name"] = squad_name
            return detail, []

        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=None),
            patch("api.v1.routes.squad.create_squad", side_effect=mock_create),
        ):
            client.post(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert "Test Manager" in captured_args["squad_name"]

    def test_uses_custom_name_when_provided(self, authed_client):
        client, _ = authed_client
        detail = _make_squad_detail()
        captured = {}

        def mock_create(db, *, user_id, season_id, player_ids, squad_name):
            captured["name"] = squad_name
            return detail, []

        payload = {**VALID_PAYLOAD, "name": "My Dream Team"}
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=None),
            patch("api.v1.routes.squad.create_squad", side_effect=mock_create),
        ):
            client.post(SQUAD_URL, json=payload, headers={"Authorization": "Bearer tok"})

        assert captured["name"] == "My Dream Team"

    def test_409_if_squad_already_exists(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=MagicMock()),
        ):
            resp = client.post(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 409
        assert "already have a squad" in resp.json()["detail"].lower()

    def test_400_with_validation_errors(self, authed_client):
        from services.squads.validation import SquadError
        client, _ = authed_client
        errors = [
            SquadError("over_budget", "Squad costs £110.0 — £10.0 over budget."),
            SquadError("wrong_position_count", "Need exactly 1 GK (you have 0)."),
        ]
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=None),
            patch("api.v1.routes.squad.create_squad", return_value=({}, errors)),
        ):
            resp = client.post(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 400
        body = resp.json()
        assert "errors" in body["detail"]
        assert len(body["detail"]["errors"]) == 2

    def test_422_if_no_player_ids_in_body(self, authed_client):
        client, _ = authed_client
        resp = client.post(SQUAD_URL, json={}, headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# PUT /squad
# ---------------------------------------------------------------------------

class TestReplaceSquad:
    def test_replaces_squad_before_lock(self, authed_client):
        client, _ = authed_client
        detail = _make_squad_detail()
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=MagicMock()),
            patch("api.v1.routes.squad.season_is_locked", return_value=False),
            patch("api.v1.routes.squad.replace_squad", return_value=(detail, [])),
        ):
            resp = client.put(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 200
        assert len(resp.json()["players"]) == 11

    def test_403_when_season_is_locked(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=MagicMock()),
            patch("api.v1.routes.squad.season_is_locked", return_value=True),
        ):
            resp = client.put(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 403
        assert "transfer" in resp.json()["detail"].lower()

    def test_404_if_no_existing_squad(self, authed_client):
        client, _ = authed_client
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=None),
        ):
            resp = client.put(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 404

    def test_400_with_validation_errors(self, authed_client):
        from services.squads.validation import SquadError
        client, _ = authed_client
        errors = [SquadError("club_limit_exceeded", "Max 2 per club (City has 3).")]
        with (
            patch("api.v1.routes.squad.get_active_season", return_value=_make_season()),
            patch("api.v1.routes.squad.get_squad_for_user", return_value=MagicMock()),
            patch("api.v1.routes.squad.season_is_locked", return_value=False),
            patch("api.v1.routes.squad.replace_squad", return_value=({}, errors)),
        ):
            resp = client.put(SQUAD_URL, json=VALID_PAYLOAD, headers={"Authorization": "Bearer tok"})

        assert resp.status_code == 400
        assert "errors" in resp.json()["detail"]

    def test_401_without_auth(self, client: TestClient):
        resp = client.put(SQUAD_URL, json=VALID_PAYLOAD)
        assert resp.status_code in (401, 403)
