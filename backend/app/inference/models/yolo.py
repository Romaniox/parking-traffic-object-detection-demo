"""Ultralytics YOLO detector (CPU).

The ultralytics/torch import is lazy so this module loads even where those heavy
packages are not installed (e.g. the lightweight test env). The model and its
weights are loaded on first inference. Default weights "yolov8n.pt" are
auto-downloaded by ultralytics on first use.
"""

from app.inference.base import Detector, RawDetection
from app.inference.classes import TARGET_CLASS_IDS

DEFAULT_WEIGHTS = "yolov8n.pt"


def _to_detections(results) -> list[RawDetection]:
    """Map an ultralytics results iterable to our RawDetection contract."""
    detections: list[RawDetection] = []
    for result in results:
        names = result.names
        for box in result.boxes:
            cls_id = int(box.cls[0])
            score = float(box.conf[0])
            x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
            detections.append(
                RawDetection(cls=names[cls_id], score=score, box=(x1, y1, x2, y2))
            )
    return detections


class YoloDetector(Detector):
    name = "yolo"

    def __init__(self, weights: str = DEFAULT_WEIGHTS, conf: float = 0.25):
        self.weights = weights
        self.conf = conf
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:  # surfaced via wrapper -> failed result + log
                # Covers a missing package AND import-time failures of its deps
                # (e.g. OpenCV needing libGL). Surface the real cause.
                raise RuntimeError(
                    f"Could not import ultralytics for the 'yolo' model: {exc}"
                ) from exc
            self._model = YOLO(self.weights)
        return self._model

    def infer(self, image) -> list[RawDetection]:
        model = self._load_model()
        results = model.predict(image, conf=self.conf, device="cpu", verbose=False, classes=TARGET_CLASS_IDS)
        return _to_detections(results)
