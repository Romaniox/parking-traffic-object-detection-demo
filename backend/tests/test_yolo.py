"""Unit tests for the YOLO detector that do NOT require ultralytics/torch.

They exercise the result-parsing logic with a fake ultralytics-like results
object, and the factory wiring. A real-inference smoke test lives separately and
is skipped unless ultralytics is installed.
"""

from app.config import Settings
from app.inference.base import RawDetection
from app.inference.models.yolo import YoloDetector, _to_detections


class _FakeArray:
    def __init__(self, values):
        self._values = values

    def __getitem__(self, idx):
        return self._values[idx]

    def __iter__(self):
        return iter(self._values)


class _FakeBox:
    def __init__(self, cls_id, conf, xyxy):
        self.cls = _FakeArray([cls_id])
        self.conf = _FakeArray([conf])
        self.xyxy = _FakeArray([_FakeArray(xyxy)])


class _FakeResult:
    def __init__(self, names, boxes):
        self.names = names
        self.boxes = boxes


def test_to_detections_maps_boxes_classes_and_scores():
    results = [
        _FakeResult(
            names={0: "person", 2: "car"},
            boxes=[
                _FakeBox(0, 0.91, [10.0, 20.0, 110.0, 220.0]),
                _FakeBox(2, 0.77, [50.0, 60.0, 150.0, 160.0]),
            ],
        )
    ]
    dets = _to_detections(results)
    assert dets == [
        RawDetection(cls="person", score=0.91, box=(10.0, 20.0, 110.0, 220.0)),
        RawDetection(cls="car", score=0.77, box=(50.0, 60.0, 150.0, 160.0)),
    ]


def test_factory_builds_yolo_with_default_weights():
    from app.inference.factory import build_wrapper

    settings = Settings(
        data_dir=None,
        max_upload_bytes=1,
        model_name="yolo",
        model_weights=None,
        database_url="sqlite:///:memory:",
    )
    wrapper = build_wrapper(settings)
    detector = wrapper._detector
    assert isinstance(detector, YoloDetector)
    assert detector.weights == "yolov8n.pt"  # auto-download default


def test_factory_uses_explicit_weights():
    from app.inference.factory import build_wrapper

    settings = Settings(
        data_dir=None,
        max_upload_bytes=1,
        model_name="yolo",
        model_weights="/models/custom.pt",
        database_url="sqlite:///:memory:",
    )
    detector = build_wrapper(settings)._detector
    assert isinstance(detector, YoloDetector)
    assert detector.weights == "/models/custom.pt"


def test_yolo_predict_passes_target_class_ids_and_imgsz():
    """infer() must forward classes=TARGET_CLASS_IDS and imgsz=1280 to model.predict."""
    from unittest.mock import MagicMock

    from PIL import Image

    from app.inference.classes import TARGET_CLASS_IDS

    fake_model = MagicMock()
    fake_model.predict.return_value = []

    detector = YoloDetector(weights="unused.pt")
    detector._model = fake_model

    img = Image.new("RGB", (320, 240))
    detector.infer(img)

    kw = fake_model.predict.call_args.kwargs
    assert kw.get("classes") == TARGET_CLASS_IDS, f"classes= not passed; got {kw}"
    assert kw.get("imgsz") == 1280, f"imgsz= not passed; got {kw}"


def test_stub_emits_only_target_classes():
    """StubDetector template must contain only TARGET_CLASSES names."""
    from PIL import Image

    from app.inference.classes import TARGET_CLASSES
    from app.inference.models.stub import StubDetector

    img = Image.new("RGB", (640, 480))
    dets = StubDetector().infer(img)
    assert dets, "stub must return at least one detection"
    bad = [d.cls for d in dets if d.cls not in TARGET_CLASSES]
    assert bad == [], f"stub emits non-target classes: {bad}"


def test_yolo_infer_without_ultralytics_raises_clear_error():
    """If ultralytics isn't installed, infer raises a clear, catchable error
    (the wrapper turns this into a failed InferenceResult)."""
    detector = YoloDetector(weights="yolov8n.pt")
    import importlib.util

    if importlib.util.find_spec("ultralytics") is not None:
        return  # installed here — covered by the smoke test instead

    try:
        detector.infer(object())  # type: ignore[arg-type]
    except RuntimeError as exc:
        assert "ultralytics" in str(exc).lower()
    else:
        raise AssertionError("expected RuntimeError when ultralytics is missing")
