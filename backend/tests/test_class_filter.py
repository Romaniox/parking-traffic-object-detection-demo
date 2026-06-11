"""Tests for the target-class filter that lives in the wrapper pipeline.

Non-target classes (anything not in TARGET_CLASSES) must be dropped before
aggregate / annotate / normalize — they must never appear in count, objects,
or boxes.
"""

import io

from PIL import Image

from app.inference.base import Detector, RawDetection
from app.inference.classes import TARGET_CLASSES, TARGET_CLASS_IDS
from app.inference.wrapper import InferenceWrapper


def _img_bytes(size=(320, 240)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (100, 100, 100)).save(buf, format="JPEG")
    return buf.getvalue()


class _FixedDetector(Detector):
    name = "fixed"

    def __init__(self, detections: list[RawDetection]):
        self._dets = detections

    def infer(self, image) -> list[RawDetection]:
        return list(self._dets)


# --- TARGET_CLASSES / TARGET_CLASS_IDS sanity ---------------------------------

def test_target_class_names():
    assert TARGET_CLASSES == frozenset({"person", "car", "motorcycle", "bus", "truck"})


def test_target_class_ids():
    assert sorted(TARGET_CLASS_IDS) == [0, 2, 3, 5, 7]


# --- wrapper filter -----------------------------------------------------------

def test_non_target_class_is_dropped():
    """A detector that emits 'dog' + 'car' → only 'car' survives."""
    det = _FixedDetector([
        RawDetection(cls="dog", score=0.9, box=(0, 0, 50, 50)),
        RawDetection(cls="car", score=0.8, box=(10, 10, 100, 100)),
    ])
    result = InferenceWrapper(det).predict(_img_bytes())

    assert result.success is True
    assert result.count == 1
    assert len(result.objects) == 1
    assert result.objects[0].cls == "car"
    assert len(result.boxes) == 1
    assert result.boxes[0].cls == "car"


def test_all_non_target_yields_zero_count():
    """All detections from outside the target set → count 0, empty lists."""
    det = _FixedDetector([
        RawDetection(cls="dog",   score=0.9, box=(0, 0, 50, 50)),
        RawDetection(cls="bird",  score=0.7, box=(60, 60, 120, 120)),
    ])
    result = InferenceWrapper(det).predict(_img_bytes())

    assert result.success is True
    assert result.count == 0
    assert result.objects == []
    assert result.boxes == []


def test_all_target_classes_pass_through():
    """All five target classes should all survive the filter."""
    dets = [
        RawDetection(cls=cls, score=0.9, box=(i * 10, 0, i * 10 + 50, 50))
        for i, cls in enumerate(["person", "car", "motorcycle", "bus", "truck"])
    ]
    det = _FixedDetector(dets)
    result = InferenceWrapper(det).predict(_img_bytes())

    assert result.success is True
    assert result.count == 5
    result_cls = {o.cls for o in result.objects}
    assert result_cls == {"person", "car", "motorcycle", "bus", "truck"}
