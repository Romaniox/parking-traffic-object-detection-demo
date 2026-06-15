from collections import Counter

from app.inference.base import DetectionObject, RawDetection


def aggregate(detections: list[RawDetection]) -> tuple[int, list[DetectionObject]]:
    """Collapse raw detections into a total count and per-class counts."""
    counts = Counter(d.cls for d in detections)
    objects = [
        DetectionObject(cls=cls, count=n)
        for cls, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    return len(detections), objects
