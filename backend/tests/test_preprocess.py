"""Tests for the preprocess pipeline stage."""

import io

import PIL.Image
import pytest
from PIL import Image

from app.inference.pipeline.preprocess import MAX_IMAGE_PIXELS, decode_image


def _png_bytes(size=(100, 100)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (128, 128, 128)).save(buf, format="PNG")
    return buf.getvalue()


def test_max_image_pixels_is_set_and_sane():
    """Decompression-bomb guard: limit must be set and well below Pillow's default 89 Mpx."""
    assert MAX_IMAGE_PIXELS is not None
    assert MAX_IMAGE_PIXELS <= 50_000_000


def test_decode_image_returns_rgb_image():
    img = decode_image(_png_bytes())
    assert img.mode == "RGB"
    assert img.size == (100, 100)


def test_decode_image_raises_on_garbage():
    with pytest.raises(Exception):
        decode_image(b"not an image")


def test_decode_image_rejects_decompression_bomb(monkeypatch):
    """An image whose pixel count exceeds the configured limit should be rejected."""
    # Temporarily lower the limit so we can trigger it with a real image.
    monkeypatch.setattr(PIL.Image, "MAX_IMAGE_PIXELS", 100)
    big = _png_bytes(size=(20, 20))  # 400 px — above the 100-px monkeypatched limit
    with pytest.raises(PIL.Image.DecompressionBombError):
        decode_image(big)
