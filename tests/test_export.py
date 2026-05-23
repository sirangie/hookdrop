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


def _seed_requests(client, count=3):
    for i in range(count):
        client.post(
            f"/hook/test-{i}",
            data=json.dumps({"index": i}),
            content_type="application/json",
        )


def test_export_json_empty(client):
    resp = client.get("/requests/export?format=json")
    assert resp.status_code == 200
    assert resp.content_type == "application/json"
    data = json.loads(resp.data)
    assert data == []


def test_export_json_with_data(client):
    _seed_requests(client, count=3)
    resp = client.get("/requests/export?format=json")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data) == 3
    assert "id" in data[0]
    assert "method" in data[0]
    assert "path" in data[0]


def test_export_json_default_format(client):
    _seed_requests(client, count=2)
    resp = client.get("/requests/export")
    assert resp.status_code == 200
    assert resp.content_type == "application/json"


def test_export_csv_empty(client):
    resp = client.get("/requests/export?format=csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.content_type
    lines = resp.data.decode("utf-8").strip().splitlines()
    assert len(lines) == 1  # header only
    assert "id" in lines[0]
    assert "method" in lines[0]


def test_export_csv_with_data(client):
    _seed_requests(client, count=4)
    resp = client.get("/requests/export?format=csv")
    assert resp.status_code == 200
    lines = resp.data.decode("utf-8").strip().splitlines()
    assert len(lines) == 5  # 1 header + 4 rows
    assert "POST" in lines[1]


def test_export_invalid_format(client):
    resp = client.get("/requests/export?format=xml")
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert "error" in data
    assert "xml" in data["error"]


def test_export_csv_content_disposition(client):
    resp = client.get("/requests/export?format=csv")
    assert "attachment" in resp.headers.get("Content-Disposition", "")
    assert "hookdrop_requests.csv" in resp.headers.get("Content-Disposition", "")


def test_export_json_content_disposition(client):
    resp = client.get("/requests/export?format=json")
    assert "attachment" in resp.headers.get("Content-Disposition", "")
    assert "hookdrop_requests.json" in resp.headers.get("Content-Disposition", "")
