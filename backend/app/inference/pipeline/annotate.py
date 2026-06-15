import io

from PIL import Image, ImageDraw, ImageFont

from app.inference.base import RawDetection

_BOX_COLOR = (255, 64, 64)
_TEXT_COLOR = (255, 255, 255)


def _font() -> ImageFont.ImageFont:
    return ImageFont.load_default()


def annotate(image: Image.Image, detections: list[RawDetection]) -> bytes:
    """Draw bounding boxes and class/score labels, return JPEG bytes."""
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    font = _font()

    for det in detections:
        x1, y1, x2, y2 = det.box
        draw.rectangle((x1, y1, x2, y2), outline=_BOX_COLOR, width=3)
        label = f"{det.cls} {det.score:.2f}"
        tb = draw.textbbox((x1, y1), label, font=font)
        draw.rectangle((tb[0], tb[1], tb[2] + 4, tb[3] + 2), fill=_BOX_COLOR)
        draw.text((x1 + 2, y1), label, fill=_TEXT_COLOR, font=font)

    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
