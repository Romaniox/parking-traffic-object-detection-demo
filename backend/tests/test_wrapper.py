import io

from PIL import Image

from app.inference.base import Detector, InferenceResult, RawDetection
from app.inference.models.stub import StubDetector
from app.inference.wrapper import InferenceWrapper


def _sample_image_bytes(size=(320, 240), color=(120, 120, 120)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()


def test_stub_through_wrapper_returns_full_result():
    wrapper = InferenceWrapper(StubDetector())
    result = wrapper.predict(_sample_image_bytes())

    assert isinstance(result, InferenceResult)
    assert result.success is True
    assert result.error is None
    assert result.count > 0
    assert result.count == sum(o.count for o in result.objects)
    assert all(o.count > 0 and o.cls for o in result.objects)

    # annotated_image must be valid JPEG bytes
    assert result.annotated_image[:2] == b"\xff\xd8"
    Image.open(io.BytesIO(result.annotated_image)).verify()

    assert "model" in result.metadata
    assert "inference_ms" in result.metadata


def test_wrapper_catches_stage_failure():
    class FailingDetector(Detector):
        name = "failing"

        def infer(self, image) -> list[RawDetection]:
            raise RuntimeError("boom")

    wrapper = InferenceWrapper(FailingDetector())
    result = wrapper.predict(_sample_image_bytes())

    assert result.success is False
    assert result.error is not None
    assert result.count == 0
    assert result.objects == []


def test_wrapper_handles_undecodable_image():
    wrapper = InferenceWrapper(StubDetector())
    result = wrapper.predict(b"not an image")

    assert result.success is False
    assert result.error is not None
