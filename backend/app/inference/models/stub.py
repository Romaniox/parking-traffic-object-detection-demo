"""Deterministic placeholder detector.

Used until a real model is selected (see SPEC "Открытые вопросы"). It returns a
fixed set of detections scaled to the input image so the full pipeline — and the
whole frontend → API → wrapper path — can be exercised without model weights.
"""

from PIL import Image

from app.inference.base import Detector, RawDetection

# Fractional boxes (x1, y1, x2, y2) relative to image size — parking scene.
_TEMPLATE: list[tuple[str, tuple[float, float, float, float]]] = [
    ("person",     (0.05, 0.10, 0.20, 0.60)),
    ("person",     (0.22, 0.12, 0.37, 0.62)),
    ("car",        (0.40, 0.40, 0.70, 0.80)),
    ("car",        (0.72, 0.38, 0.98, 0.78)),
    ("bus",        (0.02, 0.35, 0.38, 0.90)),
    ("motorcycle", (0.55, 0.55, 0.68, 0.75)),
    ("truck",      (0.60, 0.30, 0.95, 0.70)),
]


class StubDetector(Detector):
    name = "stub"

    def infer(self, image: Image.Image) -> list[RawDetection]:
        w, h = image.size
        return [
            RawDetection(
                cls=cls,
                score=0.99,
                box=(x1 * w, y1 * h, x2 * w, y2 * h),
            )
            for cls, (x1, y1, x2, y2) in _TEMPLATE
        ]
