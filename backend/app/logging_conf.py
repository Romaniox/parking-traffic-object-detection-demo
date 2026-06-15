"""Structured (JSON) logging for the service.

Each /detect request emits one record carrying the fields required by SPEC §6:
request_time, file_id, filename, status, inference_ms, error.
"""

import json
import logging
import sys
from datetime import UTC, datetime

LOGGER_NAME = "detect"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "time": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        detect = getattr(record, "detect", None)
        if isinstance(detect, dict):
            payload.update(detect)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:  # idempotent across app re-creation
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = True  # allow pytest caplog / root capture


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def log_request(
    *,
    file_id: str,
    filename: str | None,
    status: str,
    inference_ms: float | None = None,
    error: str | None = None,
) -> None:
    """Emit one structured record for a /detect request."""
    get_logger().info(
        "detect",
        extra={
            "detect": {
                "request_time": datetime.now(tz=UTC).isoformat(),
                "file_id": file_id,
                "filename": filename,
                "status": status,
                "inference_ms": inference_ms,
                "error": error,
            }
        },
    )
