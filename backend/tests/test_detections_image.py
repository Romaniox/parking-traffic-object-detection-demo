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


def test_serves_annotated_and_original(client):
    body = client.post(
        "/detect", files={"image": ("p.png", _png_bytes(), "image/png")}
    ).json()
    detection_id = body["image_url"].split("/")[2]

    annotated = client.get(f"/detections/{detection_id}/image")
    assert annotated.status_code == 200
    assert annotated.content[:2] == b"\xff\xd8"  # JPEG

    original = client.get(f"/detections/{detection_id}/image?variant=original")
    assert original.status_code == 200
    assert original.content[:8].startswith(b"\x89PNG")


def test_missing_detection_returns_404(client):
    assert client.get("/detections/does-not-exist/image").status_code == 404
