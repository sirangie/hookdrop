import pytest
from hookdrop.app import create_app
from hookdrop.storage import WebhookRequest
import time


@pytest.fixture
def app():
    return create_app(max_requests=50)


@pytest.fixture
def client(app):
    return app.test_client()


def _seed(app):
    store = app.config["store"]
    store.add(WebhookRequest(
        id="aaa", method="POST", path="/hook/payments",
        headers={"Content-Type": "application/json", "X-Source": "stripe"},
        body='{"amount": 100}', timestamp=time.time()
    ))
    store.add(WebhookRequest(
        id="bbb", method="GET", path="/hook/ping",
        headers={"Content-Type": "text/plain"},
        body="hello world", timestamp=time.time()
    ))
    store.add(WebhookRequest(
        id="ccc", method="POST", path="/hook/orders",
        headers={"Content-Type": "application/json", "X-Source": "shopify"},
        body='{"order_id": 42}', timestamp=time.time()
    ))


def test_search_no_params(client):
    resp = client.get("/search")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_search_by_path(client, app):
    _seed(app)
    resp = client.get("/search?path_contains=payments")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 1
    assert data["results"][0]["id"] == "aaa"


def test_search_by_body(client, app):
    _seed(app)
    resp = client.get("/search?body_contains=order_id")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 1
    assert data["results"][0]["id"] == "ccc"


def test_search_by_header_key(client, app):
    _seed(app)
    resp = client.get("/search?header_key=X-Source")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 2


def test_search_by_header_key_and_value(client, app):
    _seed(app)
    resp = client.get("/search?header_key=X-Source&header_value=shopify")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 1
    assert data["results"][0]["id"] == "ccc"


def test_search_no_match(client, app):
    _seed(app)
    resp = client.get("/search?body_contains=nonexistent")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 0
    assert data["results"] == []


def test_search_empty_store(client):
    resp = client.get("/search?path_contains=hook")
    assert resp.status_code == 200
    assert resp.get_json()["count"] == 0
