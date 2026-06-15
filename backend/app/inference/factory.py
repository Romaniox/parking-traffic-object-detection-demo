from app.config import Settings
from app.inference.models.stub import StubDetector
from app.inference.models.yolo import DEFAULT_WEIGHTS, YoloDetector
from app.inference.wrapper import InferenceWrapper


def build_wrapper(settings: Settings) -> InferenceWrapper:
    """Construct the inference wrapper for the configured model.

    Selected via MODEL_NAME; the external API/contract is unchanged regardless
    of the model. "yolo" uses MODEL_WEIGHTS if set, else auto-downloads the
    default YOLOv8n weights.
    """
    name = settings.model_name.lower()
    if name == "stub":
        return InferenceWrapper(StubDetector())
    if name == "yolo":
        return InferenceWrapper(YoloDetector(weights=settings.model_weights or DEFAULT_WEIGHTS))
    raise ValueError(
        f"Unknown MODEL_NAME={settings.model_name!r}; supported: 'stub', 'yolo'"
    )
