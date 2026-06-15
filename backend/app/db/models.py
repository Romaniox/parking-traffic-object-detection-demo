from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.engine import Base


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
    original_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    original_path: Mapped[str] = mapped_column(String)
    annotated_path: Mapped[str | None] = mapped_column(String, nullable=True)
    model_name: Mapped[str] = mapped_column(String)
    model_weights: Mapped[str | None] = mapped_column(String, nullable=True)
    count: Mapped[int] = mapped_column(default=0)
    inference_ms: Mapped[float | None] = mapped_column(nullable=True)
    image_width: Mapped[int | None] = mapped_column(nullable=True)
    image_height: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String)
    error: Mapped[str | None] = mapped_column(String, nullable=True)

    objects: Mapped[list["DetectionObject"]] = relationship(
        back_populates="detection",
        cascade="all, delete-orphan",
        order_by="DetectionObject.id",
    )
    boxes: Mapped[list["DetectionBox"]] = relationship(
        back_populates="detection",
        cascade="all, delete-orphan",
        order_by="DetectionBox.id",
    )


class DetectionObject(Base):
    __tablename__ = "detection_objects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    detection_id: Mapped[str] = mapped_column(ForeignKey("detections.id"))
    cls: Mapped[str] = mapped_column(String)
    count: Mapped[int] = mapped_column()

    detection: Mapped[Detection] = relationship(back_populates="objects")


class DetectionBox(Base):
    __tablename__ = "detection_boxes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    detection_id: Mapped[str] = mapped_column(ForeignKey("detections.id"))
    cls: Mapped[str] = mapped_column(String)
    conf: Mapped[float] = mapped_column(Float)
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    w: Mapped[float] = mapped_column(Float)
    h: Mapped[float] = mapped_column(Float)

    detection: Mapped[Detection] = relationship(back_populates="boxes")
