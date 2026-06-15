import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.db import repository
from app.inference.base import Detector, RawDetection
from app.inference.wrapper import InferenceWrapper
from app.main import create_app


def _png_bytes(size=(200, 150)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (90, 90, 90)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        data_dir=tmp_path,
        max_upload_bytes=10 * 1024 * 1024,
        model_name="stub",
        model_weights=None,
        database_url=f"sqlite:///{tmp_path / 'db' / 'app.db'}",
    )


@pytest.fixture
def client(settings) -> TestClient:
    return TestClient(create_app(settings))


def test_detect_success(client, settings):
    resp = client.post("/detect", files={"image": ("p.png", _png_bytes(), "image/png")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["count"] == sum(o["count"] for o in body["objects"])
    assert body["count"] > 0
    assert body["objects"][0].keys() == {"class", "count"}

    # normalized boxes for client-side overlay rendering
    assert len(body["boxes"]) == body["count"]
    b = body["boxes"][0]
    assert b.keys() == {"class", "conf", "x", "y", "w", "h"}
    assert all(0.0 <= b[k] <= 1.0 for k in ("conf", "x", "y", "w", "h"))

    # new metadata fields added to the response
    assert body["image_width"] == 200
    assert body["image_height"] == 150
    assert body["model_name"] == "stub"

    # image_url now points at the DB-backed serving endpoint
    assert body["image_url"].startswith("/detections/")
    img = client.get(body["image_url"])
    assert img.status_code == 200
    assert img.content[:2] == b"\xff\xd8"

    # files persisted under the date-partitioned images dir
    detection_id = body["image_url"].split("/")[2]
    images = list((settings.data_dir / "images").rglob("*"))
    assert any(p.name == "original.png" for p in images)
    assert any(p.name == "annotated.jpg" for p in images)

    # a DB row exists with matching metadata
    factory = client.app.state.session_factory
    with factory() as session:
        row = repository.get_detection(session, detection_id)
        assert row is not None
        assert row.status == "success"
        assert row.count == body["count"]
        assert {(o.cls, o.count) for o in row.objects} == {
            (o["class"], o["count"]) for o in body["objects"]
        }


def test_detect_rejects_unsupported_format(client):
    resp = client.post("/detect", files={"image": ("note.txt", b"hello", "text/plain")})
    assert resp.status_code == 400
    assert resp.json() == {"success": False, "error": "Unsupported file format"}


def test_detect_inference_failure_returns_500_and_records_error(settings):
    class FailingDetector(Detector):
        name = "failing"

        def infer(self, image) -> list[RawDetection]:
            raise RuntimeError("boom")

    app = create_app(settings)
    app.state.wrapper = InferenceWrapper(FailingDetector())
    client = TestClient(app, raise_server_exceptions=False)

    resp = client.post("/detect", files={"image": ("p.png", _png_bytes(), "image/png")})
    assert resp.status_code == 500
    assert resp.json() == {"success": False, "error": "Inference failed"}

    with app.state.session_factory() as session:
        rows = repository.list_detections(session)
        assert len(rows) == 1
        assert rows[0].status == "error"
