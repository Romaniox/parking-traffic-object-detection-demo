import pytest

from app.api.validation import UploadValidationError, validate_upload
from app.config import Settings


def _settings(tmp_path, max_bytes=1024):
    return Settings(
        data_dir=tmp_path,
        max_upload_bytes=max_bytes,
        model_name="stub",
        model_weights=None,
        database_url=f"sqlite:///{tmp_path / 'db' / 'app.db'}",
    )


def test_accepts_jpeg(tmp_path):
    ext = validate_upload("photo.jpg", "image/jpeg", b"x" * 10, _settings(tmp_path))
    assert ext == "jpg"


def test_accepts_png(tmp_path):
    ext = validate_upload("photo.PNG", "image/png", b"x" * 10, _settings(tmp_path))
    assert ext == "png"


def test_rejects_unsupported_extension(tmp_path):
    with pytest.raises(UploadValidationError) as exc:
        validate_upload("doc.txt", "text/plain", b"x", _settings(tmp_path))
    assert exc.value.status_code == 400
    assert exc.value.message == "Unsupported file format"


def test_rejects_mismatched_mime(tmp_path):
    with pytest.raises(UploadValidationError):
        validate_upload("photo.jpg", "application/octet-stream", b"x", _settings(tmp_path))


def test_rejects_oversized_file(tmp_path):
    with pytest.raises(UploadValidationError) as exc:
        validate_upload("photo.jpg", "image/jpeg", b"x" * 5000, _settings(tmp_path, max_bytes=1024))
    assert exc.value.status_code == 413
