"""
Verifies that /detect runs inference in a thread pool rather than blocking
the async event loop.

Strategy: run the request inside an actual async context (httpx AsyncClient)
so we know exactly which thread is the event-loop thread. The injected
detector records its own thread; we assert it differs from the loop thread.
"""

import asyncio
import io
import threading

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.config import Settings
from app.inference.base import Detector, RawDetection
from app.inference.wrapper import InferenceWrapper
from app.main import create_app


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (50, 50), (0, 0, 0)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        data_dir=tmp_path,
        max_upload_bytes=10 * 1024 * 1024,
        model_name="stub",
        model_weights=None,
        database_url=f"sqlite:///{tmp_path / 'db' / 'app.db'}",
    )


def test_inference_runs_outside_event_loop_thread(settings):
    """wrapper.predict must not execute on the event-loop thread itself."""
    infer_thread_box: list[threading.Thread] = []
    loop_thread_box: list[threading.Thread] = []

    class ThreadRecordingDetector(Detector):
        name = "thread-recorder"

        def infer(self, image) -> list[RawDetection]:
            infer_thread_box.append(threading.current_thread())
            return []

    app = create_app(settings)
    app.state.wrapper = InferenceWrapper(ThreadRecordingDetector())

    async def _run():
        # Capture the event-loop thread before any I/O.
        loop_thread_box.append(threading.current_thread())
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/detect",
                files={"image": ("p.png", _png_bytes(), "image/png")},
            )
        return resp

    resp = asyncio.run(_run())

    assert resp.status_code == 200
    assert infer_thread_box, "infer() was never called"
    assert loop_thread_box, "loop thread not captured"

    loop_thread = loop_thread_box[0]
    infer_thread = infer_thread_box[0]
    assert infer_thread is not loop_thread, (
        f"infer() ran on the event-loop thread ({loop_thread.name}) — "
        "this blocks all concurrent requests during inference"
    )
