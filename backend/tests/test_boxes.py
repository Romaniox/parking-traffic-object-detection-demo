import io

from PIL import Image

from app.inference.base import NormalizedBox, RawDetection, normalize_detection
from app.inference.models.stub import StubDetector
from app.inference.wrapper import InferenceWrapper


def _sample_jpeg(size=(320, 240)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (120, 120, 120)).save(buf, format="JPEG")
    return buf.getvalue()


def test_normalize_detection_maps_pixels_to_fractions():
    det = RawDetection(cls="person", score=0.9, box=(10.0, 20.0, 110.0, 220.0))
    nb = normalize_detection(det, width=200, height=400)
    assert isinstance(nb, NormalizedBox)
    assert nb.cls == "person"
    assert nb.conf == 0.9
    assert nb.x == 0.05  # 10/200
    assert nb.y == 0.05  # 20/400
    assert nb.w == 0.5  # (110-10)/200
    assert nb.h == 0.5  # (220-20)/400


def test_normalize_detection_clamps_out_of_bounds():
    det = RawDetection(cls="car", score=1.2, box=(-10.0, -5.0, 260.0, 130.0))
    nb = normalize_detection(det, width=200, height=100)
    assert 0.0 <= nb.x <= 1.0
    assert 0.0 <= nb.y <= 1.0
    assert nb.x + nb.w <= 1.0 + 1e-9
    assert nb.y + nb.h <= 1.0 + 1e-9
    assert 0.0 <= nb.conf <= 1.0


def test_wrapper_includes_normalized_boxes():
    result = InferenceWrapper(StubDetector()).predict(_sample_jpeg())
    assert result.success is True
    assert len(result.boxes) == result.count
    for b in result.boxes:
        assert isinstance(b, NormalizedBox)
        assert 0.0 <= b.x <= 1.0 and 0.0 <= b.y <= 1.0
        assert 0.0 <= b.w <= 1.0 and 0.0 <= b.h <= 1.0
        assert 0.0 <= b.conf <= 1.0
        assert b.cls
