"""
Health and info route tests.

These are unit tests — they use the mocked DB client from conftest.py
and do not require a running PostgreSQL instance.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    """Health endpoint returns 200 and correct shape when DB is reachable."""
    with patch("api.v1.routes.health.check_db_connection", return_value=True):
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert "version" in body


def test_health_degraded(client: TestClient) -> None:
    """Health endpoint returns degraded status when DB is unreachable."""
    with patch("api.v1.routes.health.check_db_connection", return_value=False):
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "unreachable"


def test_api_info(client: TestClient) -> None:
    """Info endpoint returns expected metadata fields."""
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Top5 Fantasy API"
    assert "version" in body
