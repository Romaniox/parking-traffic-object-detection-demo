from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Detection, DetectionBox, DetectionObject

# (cls, conf, x, y, w, h)
BoxTuple = tuple[str, float, float, float, float, float]


def create_detection(
    session: Session,
    *,
    detection_id: str,
    original_filename: str | None,
    original_path: str,
    annotated_path: str | None,
    model_name: str,
    model_weights: str | None,
    count: int,
    objects: Sequence[tuple[str, int]],
    boxes: Sequence[BoxTuple] = (),
    inference_ms: float | None,
    image_width: int | None,
    image_height: int | None,
    status: str,
    error: str | None,
) -> Detection:
    detection = Detection(
        id=detection_id,
        original_filename=original_filename,
        original_path=original_path,
        annotated_path=annotated_path,
        model_name=model_name,
        model_weights=model_weights,
        count=count,
        inference_ms=inference_ms,
        image_width=image_width,
        image_height=image_height,
        status=status,
        error=error,
        objects=[DetectionObject(cls=cls, count=n) for cls, n in objects],
        boxes=[
            DetectionBox(cls=cls, conf=conf, x=x, y=y, w=w, h=h)
            for cls, conf, x, y, w, h in boxes
        ],
    )
    session.add(detection)
    session.flush()
    return detection


def get_detection(session: Session, detection_id: str) -> Detection | None:
    return session.get(Detection, detection_id)


def list_detections(session: Session, *, limit: int = 50, offset: int = 0) -> Sequence[Detection]:
    # selectinload emits a single IN-query for all child objects instead of
    # one query per row (N+1 pattern).
    stmt = (
        select(Detection)
        .options(selectinload(Detection.objects))
        .order_by(Detection.created_at.desc(), Detection.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return session.execute(stmt).scalars().all()
