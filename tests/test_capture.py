"""Tests for webhook capture storage and routes."""

import pytest
from flask import Flask
from hookdrop.storage import RequestStore, WebhookRequest
from hookdrop.routes.capture import capture_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(capture_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# --- Storage unit tests ---

def test_store_add_and_retrieve():
    s = RequestStore()
    req = WebhookRequest("POST", "/test", {"Content-Type": "application/json"}, b'{"x": 1}')
    s.add(req)
    assert len(s) == 1
    assert s.get_by_id(req.id) is req


def test_store_max_requests():
    s = RequestStore(max_requests=3)
    for i in range(5):
        s.add(WebhookRequest("GET", f"/p{i}", {}, b""))
    assert len(s) == 3


def test_store_clear():
    s = RequestStore()
    s.add(WebhookRequest("GET", "/a", {}, b""))
    count = s.clear()
    assert count == 1
    assert len(s) == 0


def test_to_dict_fields():
    req = WebhookRequest("POST", "/hook", {"X-Custom": "val"}, b"hello", "foo=bar")
    d = req.to_dict()
    assert d["method"] == "POST"
    assert d["body"] == "hello"
    assert d["query_string"] == "foo=bar"
    assert "received_at" in d


# --- Route integration tests ---

def test_capture_endpoint(client):
    resp = client.post("/hooks/github/push", data=b'{"event": "push"}',
                       content_type="application/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "captured"
    assert "id" in data


def test_list_requests(client):
    client.post("/hooks/test", data=b"ping")
    resp = client.get("/api/requests")
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_request_not_found(client):
    resp = client.get("/api/requests/nonexistent-id")
    assert resp.status_code == 404


def test_clear_requests(client):
    client.post("/hooks/clear-test", data=b"data")
    resp = client.delete("/api/requests")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] >= 1
