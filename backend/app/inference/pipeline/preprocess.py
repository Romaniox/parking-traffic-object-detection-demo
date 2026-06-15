import io

import PIL.Image
from PIL import Image

# Decompression-bomb guard: reject images whose uncompressed pixel count exceeds
# this limit.  Pillow's built-in default is 89 Mpx; we tighten it to 50 Mpx
# (~7700×6500 px) which is more than enough for object-detection inputs.
MAX_IMAGE_PIXELS = 50_000_000
PIL.Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def decode_image(data: bytes) -> Image.Image:
    """Decode raw bytes into an RGB image. Raises if the bytes are not an image.

    Raises PIL.Image.DecompressionBombError if the image exceeds MAX_IMAGE_PIXELS.
    """
    image = Image.open(io.BytesIO(data))
    image.load()
    return image.convert("RGB")
