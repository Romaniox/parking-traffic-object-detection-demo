import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (160, 120), (40, 40, 40)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def client(tmp_path) -> TestClient:
    settings = Settings(
        data_dir=tmp_path,
        max_upload_bytes=10 * 1024 * 1024,
        model_name="stub",
        model_weights=None,
        database_url=f"sqlite:///{tmp_path / 'db' / 'app.db'}",
    )
    return TestClient(create_app(settings))


def _detect(client, name):
    return client.post("/detect", files={"image": (name, _png_bytes(), "image/png")}).json()


def test_list_returns_newest_first_with_pagination(client):
    ids = [_detect(client, f"{i}.png")["image_url"].split("/")[2] for i in range(3)]

    resp = client.get("/detections?limit=2&offset=0")
    assert resp.status_code == 200
    body = resp.json()
    assert [item["id"] for item in body["items"]] == [ids[2], ids[1]]
    # response must not leak filesystem paths
    assert "original_path" not in body["items"][0]
    assert "annotated_path" not in body["items"][0]
    assert body["items"][0]["image_url"].startswith("/detections/")

    page2 = client.get("/detections?limit=2&offset=2").json()
    assert [item["id"] for item in page2["items"]] == [ids[0]]


def test_detail_returns_objects_and_metadata(client):
    detection_id = _detect(client, "p.png")["image_url"].split("/")[2]

    resp = client.get(f"/detections/{detection_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == detection_id
    assert body["status"] == "success"
    assert body["count"] == sum(o["count"] for o in body["objects"])
    assert body["objects"][0].keys() == {"class", "count"}
    assert "original_path" not in body
    assert "annotated_path" not in body

    # detail carries persisted boxes
    assert len(body["boxes"]) == body["count"]
    assert body["boxes"][0].keys() == {"class", "conf", "x", "y", "w", "h"}


def test_list_omits_boxes(client):
    _detect(client, "p.png")
    item = client.get("/detections").json()["items"][0]
    assert "boxes" not in item


def test_detail_missing_returns_404(client):
    assert client.get("/detections/nope").status_code == 404
