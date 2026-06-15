import io
import json
import logging

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.logging_conf import LOGGER_NAME, JsonFormatter
from app.main import create_app

REQUIRED_FIELDS = {"request_time", "file_id", "filename", "status", "inference_ms", "error"}


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (120, 90), (60, 60, 60)).save(buf, format="PNG")
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


def test_json_formatter_emits_valid_json_with_fields():
    record = logging.makeLogRecord(
        {
            "name": LOGGER_NAME,
            "levelname": "INFO",
            "msg": "detect",
            "detect": {
                "request_time": "2026-05-25T00:00:00Z",
                "file_id": "abc",
                "filename": "p.png",
                "status": "success",
                "inference_ms": 12.3,
                "error": None,
            },
        }
    )
    payload = json.loads(JsonFormatter().format(record))
    assert REQUIRED_FIELDS <= payload.keys()
    assert payload["status"] == "success"
    assert payload["file_id"] == "abc"


def test_detect_logs_success(settings, caplog):
    client = TestClient(create_app(settings))
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        client.post("/detect", files={"image": ("p.png", _png_bytes(), "image/png")})

    records = [r for r in caplog.records if r.name == LOGGER_NAME]
    assert records, "expected a detect log record"
    info = records[-1].detect
    assert REQUIRED_FIELDS <= info.keys()
    assert info["status"] == "success"
    assert info["filename"] == "p.png"
    assert info["file_id"]
    assert isinstance(info["inference_ms"], int | float)


def test_detect_logs_rejected_request(settings, caplog):
    client = TestClient(create_app(settings))
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        client.post("/detect", files={"image": ("note.txt", b"hello", "text/plain")})

    records = [r for r in caplog.records if r.name == LOGGER_NAME]
    assert records
    info = records[-1].detect
    assert info["status"] == "rejected"
    assert info["error"] == "Unsupported file format"
