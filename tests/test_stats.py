import pytest
from hookdrop.app import create_app
from hookdrop.storage import RequestStore


@pytest.fixture
def app():
    store = RequestStore(max_requests=100)
    application = create_app(store=store)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def _seed(client, method="POST", content_type="application/json", body=b'{"x": 1}'):
    return client.open(
        "/hooks/test",
        method=method,
        data=body,
        headers={"Content-Type": content_type},
    )


def test_stats_empty(client):
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 0
    assert data["by_method"] == {}
    assert data["most_recent"] is None


def test_stats_total(client):
    _seed(client)
    _seed(client)
    resp = client.get("/stats")
    data = resp.get_json()
    assert data["total"] == 2


def test_stats_by_method(client):
    _seed(client, method="POST")
    _seed(client, method="POST")
    _seed(client, method="GET", body=b"")
    resp = client.get("/stats")
    data = resp.get_json()
    assert data["by_method"]["POST"] == 2
    assert data["by_method"]["GET"] == 1


def test_stats_by_content_type(client):
    _seed(client, content_type="application/json")
    _seed(client, content_type="text/plain", body=b"hello")
    resp = client.get("/stats")
    data = resp.get_json()
    assert data["by_content_type"]["application/json"] == 1
    assert data["by_content_type"]["text/plain"] == 1


def test_stats_most_recent(client):
    _seed(client)
    r2 = _seed(client)
    resp = client.get("/stats")
    data = resp.get_json()
    assert data["most_recent"] is not None
    assert isinstance(data["most_recent"], str)
