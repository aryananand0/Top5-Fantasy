"""
Auth route unit tests.

All tests use mocked service functions — no real database required.
Service functions are patched at the route module level (where they're imported).
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from core.dependencies import _get_current_user
from main import app
from tests.conftest import make_mock_user

SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"

VALID_SIGNUP = {
    "email": "player@example.com",
    "username": "player_one",
    "password": "securepass123",
}


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_success(self, client: TestClient) -> None:
        mock_user = make_mock_user()
        with (
            patch("api.v1.routes.auth.get_user_by_email", return_value=None),
            patch("api.v1.routes.auth.get_user_by_username", return_value=None),
            patch("api.v1.routes.auth.create_user", return_value=mock_user),
        ):
            resp = client.post(SIGNUP_URL, json=VALID_SIGNUP)

        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == mock_user.email
        assert body["username"] == mock_user.username
        # password_hash must NEVER appear in any response
        assert "password_hash" not in body
        assert "password" not in body

    def test_duplicate_email(self, client: TestClient) -> None:
        with patch("api.v1.routes.auth.get_user_by_email", return_value=make_mock_user()):
            resp = client.post(SIGNUP_URL, json=VALID_SIGNUP)
        assert resp.status_code == 409
        assert "email" in resp.json()["detail"].lower()

    def test_duplicate_username(self, client: TestClient) -> None:
        with (
            patch("api.v1.routes.auth.get_user_by_email", return_value=None),
            patch("api.v1.routes.auth.get_user_by_username", return_value=make_mock_user()),
        ):
            resp = client.post(SIGNUP_URL, json=VALID_SIGNUP)
        assert resp.status_code == 409
        assert "username" in resp.json()["detail"].lower()

    def test_invalid_password_too_short(self, client: TestClient) -> None:
        payload = {**VALID_SIGNUP, "password": "short"}
        resp = client.post(SIGNUP_URL, json=payload)
        assert resp.status_code == 422

    def test_invalid_username_special_chars(self, client: TestClient) -> None:
        payload = {**VALID_SIGNUP, "username": "bad username!"}
        resp = client.post(SIGNUP_URL, json=payload)
        assert resp.status_code == 422

    def test_invalid_email(self, client: TestClient) -> None:
        payload = {**VALID_SIGNUP, "email": "not-an-email"}
        resp = client.post(SIGNUP_URL, json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_success_with_email(self, client: TestClient) -> None:
        with patch("api.v1.routes.auth.authenticate_user", return_value=make_mock_user()):
            resp = client.post(LOGIN_URL, json={"login": "player@example.com", "password": "pass"})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert "password" not in body

    def test_success_with_username(self, client: TestClient) -> None:
        with patch("api.v1.routes.auth.authenticate_user", return_value=make_mock_user()):
            resp = client.post(LOGIN_URL, json={"login": "player_one", "password": "pass"})
        assert resp.status_code == 200

    def test_invalid_credentials(self, client: TestClient) -> None:
        with patch("api.v1.routes.auth.authenticate_user", return_value=None):
            resp = client.post(LOGIN_URL, json={"login": "player@example.com", "password": "wrong"})
        assert resp.status_code == 401
        # Generic message — must not reveal whether the account exists
        assert "invalid" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class TestLogout:
    def test_logout_always_succeeds(self, client: TestClient) -> None:
        resp = client.post(LOGOUT_URL)
        assert resp.status_code == 200
        assert "message" in resp.json()


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------

class TestMe:
    @pytest.fixture
    def authed_client(self, client: TestClient) -> tuple[TestClient, MagicMock]:
        """Client with CurrentUser dependency overridden to a mock user."""
        mock_user = make_mock_user()
        app.dependency_overrides[_get_current_user] = lambda: mock_user
        return client, mock_user

    def test_me_success(self, authed_client: tuple) -> None:
        client, mock_user = authed_client
        resp = client.get(ME_URL, headers={"Authorization": "Bearer anytoken"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == mock_user.email
        assert body["username"] == mock_user.username
        assert "password_hash" not in body

    def test_me_no_token(self, client: TestClient) -> None:
        # No Authorization header — HTTPBearer rejects the request (401 in FastAPI 0.115+)
        resp = client.get(ME_URL)
        assert resp.status_code in (401, 403)

    def test_me_invalid_token(self, client: TestClient) -> None:
        # Token present but decode returns None → 401
        with patch("core.dependencies.decode_access_token", return_value=None):
            resp = client.get(ME_URL, headers={"Authorization": "Bearer badtoken"})
        assert resp.status_code == 401
