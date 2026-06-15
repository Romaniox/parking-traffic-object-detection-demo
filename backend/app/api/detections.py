from collections.abc import Iterator
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import storage
from app.db import repository
from app.db.models import Detection

router = APIRouter()


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


def _serialize(d: Detection, *, include_boxes: bool = False) -> dict:
    """Client-facing view. Deliberately omits filesystem paths (SPEC-storage §6)."""
    view = {
        "id": d.id,
        "created_at": d.created_at.isoformat(),
        "original_filename": d.original_filename,
        "model_name": d.model_name,
        "model_weights": d.model_weights,
        "count": d.count,
        "objects": [{"class": o.cls, "count": o.count} for o in d.objects],
        "inference_ms": d.inference_ms,
        "image_width": d.image_width,
        "image_height": d.image_height,
        "status": d.status,
        "error": d.error,
        "image_url": storage.image_url(d.id),
    }
    if include_boxes:
        view["boxes"] = [
            {"class": b.cls, "conf": b.conf, "x": b.x, "y": b.y, "w": b.w, "h": b.h}
            for b in d.boxes
        ]
    return view


@router.get("/detections")
def list_detections(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> dict:
    rows = repository.list_detections(session, limit=limit, offset=offset)
    return {"items": [_serialize(r) for r in rows], "limit": limit, "offset": offset}


@router.get("/detections/{detection_id}")
def get_detection(detection_id: str, session: Session = Depends(get_session)) -> dict:
    detection = repository.get_detection(session, detection_id)
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return _serialize(detection, include_boxes=True)


@router.get("/detections/{detection_id}/image")
def get_detection_image(
    detection_id: str,
    variant: str = Query("annotated", pattern="^(annotated|original)$"),
    session: Session = Depends(get_session),
) -> FileResponse:
    detection = repository.get_detection(session, detection_id)
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")

    path_str = detection.annotated_path if variant == "annotated" else detection.original_path
    if not path_str or not Path(path_str).exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(path_str)
