import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_index_returns_service_metadata(client):
    result = client.get("/")

    assert result.status_code == 200
    assert result.json["service"] == "SecurePipeline"
    assert "version" in result.json


def test_health_endpoint(client):
    result = client.get("/health")

    assert result.status_code == 200
    assert result.json == {"service": "securepipeline", "status": "healthy"}


def test_readiness_endpoint(client):
    result = client.get("/ready")

    assert result.status_code == 200
    assert result.json["status"] == "ready"
    assert "timestamp" in result.json


def test_metrics_endpoint(client):
    result = client.get("/metrics")

    assert result.status_code == 200
    assert b"securepipeline_http_requests_total" in result.data


def test_unknown_endpoint_returns_json_404(client):
    result = client.get("/missing")

    assert result.status_code == 404
    assert result.json["error"] == "resource not found"
