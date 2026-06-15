"""Inference contract shared by the API and every detector implementation.

The external API and frontend depend only on `InferenceResult` and on the
`InferenceWrapper` that produces it — never on a concrete model. A new model is
added by implementing `Detector.infer`; the surrounding pipeline stages
(preprocess / postprocess / annotate) stay unchanged.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from PIL import Image

Box = tuple[float, float, float, float]  # x1, y1, x2, y2 in pixels


@dataclass(frozen=True)
class RawDetection:
    """A single detected instance, as produced by a model."""

    cls: str
    score: float
    box: Box


@dataclass(frozen=True)
class DetectionObject:
    """Per-class aggregation returned to the client."""

    cls: str
    count: int


@dataclass(frozen=True)
class NormalizedBox:
    """A detection box in fractions of the image size (0..1), for client rendering.

    x, y — top-left corner; w, h — width/height as fractions; conf — confidence.
    """

    cls: str
    conf: float
    x: float
    y: float
    w: float
    h: float


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def normalize_detection(det: RawDetection, width: int, height: int) -> NormalizedBox:
    """Convert a pixel-space RawDetection into a clamped 0..1 NormalizedBox."""
    x1, y1, x2, y2 = det.box
    x = _clamp01(x1 / width)
    y = _clamp01(y1 / height)
    w = _clamp01(x2 / width) - x
    h = _clamp01(y2 / height) - y
    return NormalizedBox(
        cls=det.cls,
        conf=_clamp01(det.score),
        x=x,
        y=y,
        w=max(0.0, w),
        h=max(0.0, h),
    )


@dataclass
class InferenceResult:
    success: bool
    count: int
    objects: list[DetectionObject]
    annotated_image: bytes
    boxes: list[NormalizedBox] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    error: str | None = None


class Detector(ABC):
    """Swappable model. Implementations do raw inference only; the wrapper owns
    pre/post-processing and annotation."""

    name: str = "detector"

    @abstractmethod
    def infer(self, image: Image.Image) -> list[RawDetection]:
        """Run the model on an RGB image and return raw detections."""
        raise NotImplementedError
