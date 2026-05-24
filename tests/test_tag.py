import pytest
from hookdrop.app import create_app
from hookdrop.storage import RequestStore


@pytest.fixture
def app():
    store = RequestStore(max_requests=50)
    application = create_app(store=store)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def _seed_request(client):
    resp = client.post(
        "/hooks/test",
        json={"hello": "world"},
        headers={"X-Custom": "value"},
    )
    return resp.get_json()["id"]


def test_get_tags_not_found(client):
    resp = client.get("/requests/nonexistent/tags")
    assert resp.status_code == 404


def test_add_tags_not_found(client):
    resp = client.post("/requests/nonexistent/tags", json={"tags": ["foo"]})
    assert resp.status_code == 404


def test_add_and_get_tags(client):
    rid = _seed_request(client)
    resp = client.post(f"/requests/{rid}/tags", json={"tags": ["beta", "alpha"]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["tags"] == ["alpha", "beta"]

    resp2 = client.get(f"/requests/{rid}/tags")
    assert resp2.status_code == 200
    assert resp2.get_json()["tags"] == ["alpha", "beta"]


def test_add_tags_deduplication(client):
    rid = _seed_request(client)
    client.post(f"/requests/{rid}/tags", json={"tags": ["dup", "dup", "unique"]})
    resp = client.get(f"/requests/{rid}/tags")
    assert resp.get_json()["tags"].count("dup") == 1


def test_add_tags_invalid_payload(client):
    rid = _seed_request(client)
    resp = client.post(f"/requests/{rid}/tags", json={"tags": "not-a-list"})
    assert resp.status_code == 400


def test_remove_tags(client):
    rid = _seed_request(client)
    client.post(f"/requests/{rid}/tags", json={"tags": ["keep", "remove"]})
    resp = client.delete(f"/requests/{rid}/tags", json={"tags": ["remove"]})
    assert resp.status_code == 200
    assert resp.get_json()["tags"] == ["keep"]


def test_list_all_tags(client):
    rid1 = _seed_request(client)
    rid2 = _seed_request(client)
    client.post(f"/requests/{rid1}/tags", json={"tags": ["foo", "shared"]})
    client.post(f"/requests/{rid2}/tags", json={"tags": ["bar", "shared"]})
    resp = client.get("/tags")
    assert resp.status_code == 200
    tags = resp.get_json()["tags"]
    assert "foo" in tags
    assert "bar" in tags
    assert "shared" in tags
    assert tags == sorted(tags)


def test_list_all_tags_empty(client):
    resp = client.get("/tags")
    assert resp.status_code == 200
    assert resp.get_json()["tags"] == []
