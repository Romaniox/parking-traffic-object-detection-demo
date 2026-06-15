"""On-disk layout for stored images (SPEC-storage §3).

Files live under <data_dir>/images/<YYYY>/<MM>/<DD>/<detection_id>/, partitioned by
the UTC date of processing:
    original.<ext>   — the uploaded image
    annotated.jpg    — the image with detection overlay
"""

from datetime import datetime
from pathlib import Path

ANNOTATED_FILENAME = "annotated.jpg"


def images_root(data_dir: Path) -> Path:
    return data_dir / "images"


def image_dir(data_dir: Path, detection_id: str, created: datetime) -> Path:
    return (
        images_root(data_dir)
        / f"{created.year:04d}"
        / f"{created.month:02d}"
        / f"{created.day:02d}"
        / detection_id
    )


def save_original(
    data_dir: Path, detection_id: str, data: bytes, ext: str, created: datetime
) -> Path:
    target = image_dir(data_dir, detection_id, created) / f"original.{ext}"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def save_annotated(
    data_dir: Path, detection_id: str, data: bytes, created: datetime
) -> Path:
    target = image_dir(data_dir, detection_id, created) / ANNOTATED_FILENAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def image_url(detection_id: str) -> str:
    return f"/detections/{detection_id}/image"
