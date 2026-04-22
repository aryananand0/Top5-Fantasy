"""
Test configuration and shared fixtures.

Environment variables MUST be set before any project modules are imported,
because pydantic-settings reads them at Settings() construction time.
"""

import os
from datetime import datetime

# Set required env vars before any local imports
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost/top5fantasy_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-used-in-prod")
os.environ.setdefault("DEBUG", "false")

from typing import Any  # noqa: E402
from unittest.mock import MagicMock  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from db.session import get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
def mock_db() -> MagicMock:
    """
    A mock SQLAlchemy session for unit tests.
    Extend per-test for specific query behaviour:

        def test_example(mock_db):
            mock_db.execute.return_value.scalar_one_or_none.return_value = some_object
    """
    return MagicMock()


@pytest.fixture
def client(mock_db: MagicMock) -> TestClient:
    """
    TestClient with the DB dependency overridden to a mock session.
    Use for unit tests that do not need a running PostgreSQL instance.
    """
    def _override():
        yield mock_db

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def make_mock_user(**overrides: Any) -> MagicMock:
    """
    Returns a MagicMock shaped like a User ORM object.
    Pass keyword arguments to override individual fields.

    Usage:
        user = make_mock_user(username="jane", is_active=False)
    """
    user = MagicMock()
    defaults: dict[str, Any] = {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "display_name": "Test User",
        "avatar_url": None,
        "favorite_club": None,
        "favorite_league": None,
        "is_active": True,
        "created_at": datetime(2026, 1, 1, 12, 0, 0),
        "updated_at": datetime(2026, 1, 1, 12, 0, 0),
    }
    defaults.update(overrides)
    for key, value in defaults.items():
        setattr(user, key, value)
    return user
