import asyncio
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app import storage
from app.api.validation import UploadValidationError, validate_upload
from app.db import repository
from app.logging_conf import get_logger, log_request

router = APIRouter()


def _persist(request: Request, **kwargs) -> None:
    """Best-effort DB write. A persistence failure must not fail a successful
    inference response (SPEC-storage §6) — log and move on."""
    try:
        with request.app.state.session_factory() as session:
            repository.create_detection(session, **kwargs)
            session.commit()
    except Exception:  # noqa: BLE001 — boundary: never break the response on DB error
        get_logger().exception("failed to persist detection %s", kwargs.get("detection_id"))


@router.post("/detect")
async def detect(request: Request, image: UploadFile = File(...)) -> JSONResponse:
    settings = request.app.state.settings
    wrapper = request.app.state.wrapper
    request_id = uuid.uuid4().hex
    created = datetime.now(tz=UTC)

    data = await image.read()
    try:
        ext = validate_upload(image.filename, image.content_type, data, settings)
    except UploadValidationError as err:
        log_request(
            file_id=request_id, filename=image.filename, status="rejected", error=err.message
        )
        return JSONResponse(
            status_code=err.status_code,
            content={"success": False, "error": err.message},
        )

    original_path = storage.save_original(settings.data_dir, request_id, data, ext, created)
    # Run CPU-heavy inference in a thread-pool worker so the async event loop
    # stays free to handle other requests during the 3-8 s inference window.
    result = await asyncio.to_thread(wrapper.predict, data)
    width, height = (result.metadata.get("image_size") or [None, None])[:2]

    if not result.success:
        log_request(
            file_id=request_id,
            filename=image.filename,
            status="error",
            inference_ms=result.metadata.get("inference_ms"),
            error=result.error or "Inference failed",
        )
        _persist(
            request,
            detection_id=request_id,
            original_filename=image.filename,
            original_path=str(original_path),
            annotated_path=None,
            model_name=settings.model_name,
            model_weights=settings.model_weights,
            count=0,
            objects=[],
            inference_ms=result.metadata.get("inference_ms"),
            image_width=width,
            image_height=height,
            status="error",
            error=result.error or "Inference failed",
        )
        return JSONResponse(
            status_code=500, content={"success": False, "error": "Inference failed"}
        )

    annotated_path = storage.save_annotated(
        settings.data_dir, request_id, result.annotated_image, created
    )
    log_request(
        file_id=request_id,
        filename=image.filename,
        status="success",
        inference_ms=result.metadata.get("inference_ms"),
    )
    _persist(
        request,
        detection_id=request_id,
        original_filename=image.filename,
        original_path=str(original_path),
        annotated_path=str(annotated_path),
        model_name=settings.model_name,
        model_weights=settings.model_weights,
        count=result.count,
        objects=[(o.cls, o.count) for o in result.objects],
        boxes=[(b.cls, b.conf, b.x, b.y, b.w, b.h) for b in result.boxes],
        inference_ms=result.metadata.get("inference_ms"),
        image_width=width,
        image_height=height,
        status="success",
        error=None,
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "count": result.count,
            "objects": [{"class": o.cls, "count": o.count} for o in result.objects],
            "boxes": [
                {"class": b.cls, "conf": b.conf, "x": b.x, "y": b.y, "w": b.w, "h": b.h}
                for b in result.boxes
            ],
            "image_url": storage.image_url(request_id),
            "image_width": width,
            "image_height": height,
            "model_name": settings.model_name,
        },
    )
