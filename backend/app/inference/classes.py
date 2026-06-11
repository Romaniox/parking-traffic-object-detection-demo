"""Parking-detection target classes — single source of truth.

Only detections whose class name is in TARGET_CLASSES are forwarded by the
inference wrapper. TARGET_CLASS_IDS carries the COCO ids so the YOLO detector
can tell the model to skip other classes at inference time (efficiency).

COCO mapping used:
  0  person
  2  car
  3  motorcycle
  5  bus
  7  truck
"""

TARGET_CLASSES: frozenset[str] = frozenset({"person", "car", "motorcycle", "bus", "truck"})

# COCO numeric ids — keep in sync with TARGET_CLASSES names above.
TARGET_CLASS_IDS: list[int] = [0, 2, 3, 5, 7]
