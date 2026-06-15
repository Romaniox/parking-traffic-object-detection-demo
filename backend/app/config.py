"""Runtime configuration, sourced from environment variables.

Data lives under a single DATA_DIR with sub-areas for models, images and the
SQLite database (see SPEC-storage §3).
"""

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = frozenset({"jpg", "jpeg", "png"})
ALLOWED_MIME_TYPES = frozenset({"image/jpeg", "image/png"})


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    max_upload_bytes: int
    model_name: str  # "stub" until a real model is chosen
    model_weights: str | None
    database_url: str

    @property
    def models_dir(self) -> Path:
        return self.data_dir / "models"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "db" / "app.db"


def load_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", "data")).resolve()
    max_upload_bytes = int(os.getenv("MAX_UPLOAD_BYTES", DEFAULT_MAX_UPLOAD_BYTES))
    model_name = os.getenv("MODEL_NAME", "stub")
    model_weights = os.getenv("MODEL_WEIGHTS") or None
    database_url = os.getenv("DATABASE_URL") or f"sqlite:///{data_dir / 'db' / 'app.db'}"
    return Settings(
        data_dir=data_dir,
        max_upload_bytes=max_upload_bytes,
        model_name=model_name,
        model_weights=model_weights,
        database_url=database_url,
    )
