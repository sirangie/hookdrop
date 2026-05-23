import pytest
from unittest.mock import patch, MagicMock
from hookdrop.app import create_app


@pytest.fixture
def app():
    application = create_app(max_requests=50)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def _seed_request(client):
    """Helper: capture a webhook and return its id."""
    resp = client.post(
        "/hooks/test",
        json={"event": "ping"},
        headers={"X-Source": "pytest"},
    )
    return resp.get_json()["id"]


def test_replay_not_found(client):
    resp = client.post("/replay/nonexistent", json={"target_url": "http://example.com"})
    assert resp.status_code == 404
    assert "not found" in resp.get_json()["error"].lower()


def test_replay_missing_target_url(client):
    req_id = _seed_request(client)
    resp = client.post(f"/replay/{req_id}", json={})
    assert resp.status_code == 400
    assert "target_url" in resp.get_json()["error"]


def test_replay_success(client):
    req_id = _seed_request(client)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch("hookdrop.routes.replay.requests.request", return_value=mock_response) as mock_req:
        resp = client.post(
            f"/replay/{req_id}",
            json={"target_url": "http://localhost:5001/receive"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["replayed"] is True
        assert data["status_code"] == 200
        assert data["request_id"] == req_id
        mock_req.assert_called_once()


def test_replay_upstream_error(client):
    import requests as req_lib
    req_id = _seed_request(client)

    with patch(
        "hookdrop.routes.replay.requests.request",
        side_effect=req_lib.exceptions.ConnectionError("refused"),
    ):
        resp = client.post(
            f"/replay/{req_id}",
            json={"target_url": "http://dead-host/path"},
        )
        assert resp.status_code == 502
        assert "refused" in resp.get_json()["error"]
