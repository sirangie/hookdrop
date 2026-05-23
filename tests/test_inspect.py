import json
import pytest
from hookdrop.app import create_app
from hookdrop.storage import RequestStore


@pytest.fixture
def app():
    store = RequestStore(max_requests=50)
    application = create_app(store)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def _seed_json_request(client):
    return client.post(
        "/hooks/test",
        data=json.dumps({"event": "push", "repo": "hookdrop"}),
        content_type="application/json",
    )


def _seed_plain_request(client):
    return client.post(
        "/hooks/plain",
        data="hello world",
        content_type="text/plain",
    )


def test_inspect_not_found(client):
    resp = client.get("/inspect/nonexistent-id")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Request not found"


def test_inspect_json_request(client):
    _seed_json_request(client)
    list_resp = client.get("/requests")
    request_id = list_resp.get_json()[0]["id"]

    resp = client.get(f"/inspect/{request_id}")
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["id"] == request_id
    assert data["summary"]["method"] == "POST"
    assert data["summary"]["content_type"] == "application/json"
    assert data["summary"]["body_size_bytes"] > 0
    assert data["parsed_body"] == {"event": "push", "repo": "hookdrop"}
    assert "headers" in data
    assert "query_params" in data


def test_inspect_plain_body_not_parsed(client):
    _seed_plain_request(client)
    list_resp = client.get("/requests")
    request_id = list_resp.get_json()[0]["id"]

    resp = client.get(f"/inspect/{request_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["parsed_body"] is None
    assert data["body"] == "hello world"


def test_inspect_headers_only(client):
    _seed_json_request(client)
    list_resp = client.get("/requests")
    request_id = list_resp.get_json()[0]["id"]

    resp = client.get(f"/inspect/{request_id}/headers")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == request_id
    assert isinstance(data["headers"], dict)
    assert "Content-Type" in data["headers"]


def test_inspect_headers_not_found(client):
    resp = client.get("/inspect/bad-id/headers")
    assert resp.status_code == 404
