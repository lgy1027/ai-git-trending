"""Tests for system endpoints: /health and /api/rate-limit-status."""

from __future__ import annotations


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == 0
    assert payload["data"]["status"] == "ok"


def test_health_does_not_touch_database(client):
    # /health must respond even when the DB is unreachable — it is a liveness
    # probe, not a readiness probe. We simply assert it returns within the
    # normal Flask test-client cycle (i.e. it doesn't raise).
    response = client.get("/health")
    assert response.status_code == 200


def test_rate_limit_status_returns_copy_and_export(client):
    response = client.get("/api/rate-limit-status")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == 0
    data = payload["data"]
    assert "copy" in data
    assert "export" in data
    for key in ("limit", "remaining"):
        assert key in data["copy"]
        assert key in data["export"]


def test_legacy_routes_still_serve_through_blueprints(client):
    # Make sure the move did not change URL paths or response shapes for the
    # routes previously defined directly on `app` in `router.py`.
    response = client.get("/api/reports")
    assert response.status_code == 200
    assert response.get_json()["code"] == 0

    response = client.get("/api/report/2099-01-01")  # non-existent date
    assert response.status_code == 404

    response = client.get("/api/trends?days=7")
    assert response.status_code == 200
    assert response.get_json()["code"] == 0

    response = client.get("/api/trend-data")
    assert response.status_code == 200
    items = response.get_json()["data"]
    assert isinstance(items, list)
    labels = {item["label"] for item in items}
    assert {"热门项目", "飙升项目", "技术领域"} <= labels