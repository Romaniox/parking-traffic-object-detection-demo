from datetime import UTC, datetime
from pathlib import Path

from app import storage


def test_image_dir_is_date_partitioned():
    created = datetime(2026, 5, 26, 10, 0, 0, tzinfo=UTC)
    d = storage.image_dir(Path("/data"), "abc123", created)
    assert d == Path("/data/images/2026/05/26/abc123")


def test_save_original_and_annotated(tmp_path):
    created = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    orig = storage.save_original(tmp_path, "id1", b"\x01\x02", "png", created)
    annot = storage.save_annotated(tmp_path, "id1", b"\xff\xd8jpeg", created)

    assert orig == tmp_path / "images" / "2026" / "01" / "02" / "id1" / "original.png"
    assert annot == tmp_path / "images" / "2026" / "01" / "02" / "id1" / "annotated.jpg"
    assert orig.read_bytes() == b"\x01\x02"
    assert annot.read_bytes() == b"\xff\xd8jpeg"
