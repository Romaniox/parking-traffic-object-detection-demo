"""Real-inference smoke test. Skipped unless ultralytics is installed.

Run where torch/ultralytics are available (downloads yolov8n.pt on first run):
    pytest tests/test_yolo_smoke.py
"""

import io

import pytest
from PIL import Image

pytest.importorskip("ultralytics")

from app.inference.models.yolo import YoloDetector  # noqa: E402
from app.inference.wrapper import InferenceWrapper  # noqa: E402


@pytest.mark.smoke
def test_yolo_runs_on_a_small_image():
    buf = io.BytesIO()
    Image.new("RGB", (320, 240), (128, 128, 128)).save(buf, format="JPEG")

    result = InferenceWrapper(YoloDetector()).predict(buf.getvalue())

    assert result.success is True
    assert result.annotated_image[:2] == b"\xff\xd8"
    assert result.count == sum(o.count for o in result.objects)
    assert result.metadata["model"] == "yolo"
