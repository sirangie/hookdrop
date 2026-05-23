import pytest
from hookdrop.app import create_app
from hookdrop.storage import RequestStore


@pytest.fixture
def app():
    store = RequestStore(max_requests=50)
    return create_app(store=store)


@pytest.fixture
def client(app):
    return app.test_client()


def _seed(client, method="POST", path="/hook", headers=None, body=b"hello", status=200):
    hdrs = {"Content-Type": "text/plain"}
    if headers:
        hdrs.update(headers)
    client.open(path, method=method, data=body, headers=hdrs)


def test_filter_empty(client):
    resp = client.get("/requests/filter")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 0


def test_filter_by_method(client):
    _seed(client, method="POST", path="/a")
    _seed(client, method="GET", path="/b")
    resp = client.get("/requests/filter?method=GET")
    data = resp.get_json()
    assert data["count"] == 1
    assert data["requests"][0]["method"] == "GET"


def test_filter_by_path(client):
    _seed(client, path="/webhooks/github")
    _seed(client, path="/webhooks/stripe")
    _seed(client, path="/other")
    resp = client.get("/requests/filter?path=webhooks")
    data = resp.get_json()
    assert data["count"] == 2


def test_filter_by_header_key(client):
    _seed(client, headers={"X-Source": "github"})
    _seed(client, headers={})
    resp = client.get("/requests/filter?header_key=X-Source")
    data = resp.get_json()
    assert data["count"] == 1


def test_filter_by_header_key_and_value(client):
    _seed(client, headers={"X-Event": "push"})
    _seed(client, headers={"X-Event": "pull_request"})
    resp = client.get("/requests/filter?header_key=X-Event&header_value=push")
    data = resp.get_json()
    assert data["count"] == 1
    assert "push" in str(data["requests"][0]["headers"]).lower()


def test_filter_combined(client):
    _seed(client, method="POST", path="/hook", headers={"X-Type": "order"})
    _seed(client, method="POST", path="/hook", headers={"X-Type": "refund"})
    _seed(client, method="GET", path="/hook", headers={"X-Type": "order"})
    resp = client.get("/requests/filter?method=POST&header_key=X-Type&header_value=order")
    data = resp.get_json()
    assert data["count"] == 1


def test_filter_no_match(client):
    _seed(client, method="POST")
    resp = client.get("/requests/filter?method=DELETE")
    data = resp.get_json()
    assert data["count"] == 0
