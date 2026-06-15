from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker

from app.api.detect import router as detect_router
from app.api.detections import router as detections_router
from app.config import Settings, load_settings
from app.db.engine import init_db, make_engine
from app.inference.factory import build_wrapper
from app.logging_conf import configure_logging
from app.storage import images_root


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    configure_logging()

    # Ensure data areas exist before the DB connects.
    images_root(settings.data_dir).mkdir(parents=True, exist_ok=True)
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = make_engine(settings.database_url)
    init_db(engine)

    app = FastAPI(title="Object Detection Service")
    app.state.settings = settings
    app.state.wrapper = build_wrapper(settings)
    app.state.engine = engine
    app.state.session_factory = sessionmaker(engine, expire_on_commit=False)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(detect_router)
    app.include_router(detections_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
