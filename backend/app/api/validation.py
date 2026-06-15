from app.config import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, Settings

_EXT_ALIASES = {"jpeg": "jpg"}


class UploadValidationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_upload(
    filename: str | None,
    content_type: str | None,
    data: bytes,
    settings: Settings,
) -> str:
    """Validate an uploaded file and return its normalized extension.

    Raises UploadValidationError (400 for format, 413 for size).
    """
    ext = (filename or "").rsplit(".", 1)[-1].lower() if "." in (filename or "") else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadValidationError("Unsupported file format", 400)
    if (content_type or "").lower() not in ALLOWED_MIME_TYPES:
        raise UploadValidationError("Unsupported file format", 400)
    if len(data) == 0:
        raise UploadValidationError("Unsupported file format", 400)
    if len(data) > settings.max_upload_bytes:
        raise UploadValidationError("File too large", 413)
    return _EXT_ALIASES.get(ext, ext)
