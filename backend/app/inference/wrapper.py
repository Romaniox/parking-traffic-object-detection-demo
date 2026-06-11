import time

from app.inference.base import Detector, InferenceResult, normalize_detection
from app.inference.classes import TARGET_CLASSES
from app.inference.pipeline.annotate import annotate
from app.inference.pipeline.postprocess import aggregate
from app.inference.pipeline.preprocess import decode_image


class InferenceWrapper:
    """Single entry point the API depends on. Orchestrates the interchangeable
    pipeline stages around a swappable `Detector` and always returns an
    `InferenceResult` — failures are captured, never raised."""

    def __init__(self, detector: Detector):
        self._detector = detector

    def predict(self, image: bytes, config: dict | None = None) -> InferenceResult:
        started = time.perf_counter()
        try:
            decoded = decode_image(image)
            detections = [d for d in self._detector.infer(decoded) if d.cls in TARGET_CLASSES]
            count, objects = aggregate(detections)
            annotated = annotate(decoded, detections)
            width, height = decoded.size
            boxes = [normalize_detection(d, width, height) for d in detections]
        except Exception as exc:  # noqa: BLE001 — boundary: any stage failure → result
            return InferenceResult(
                success=False,
                count=0,
                objects=[],
                annotated_image=b"",
                metadata={"model": self._detector.name},
                error=str(exc),
            )

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return InferenceResult(
            success=True,
            count=count,
            objects=objects,
            annotated_image=annotated,
            boxes=boxes,
            metadata={
                "model": self._detector.name,
                "inference_ms": elapsed_ms,
                "image_size": list(decoded.size),
            },
        )
