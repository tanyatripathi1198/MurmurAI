import os
from pathlib import Path
from typing import Callable, Optional
import numpy as np
import sounddevice as sd

try:
    from openwakeword.model import Model as _OWWModel
except ImportError:
    _OWWModel = None   # graceful degradation if not installed

MODEL_PATH = Path(os.environ.get("APPDATA", Path.home())) / "Pooky" / "Hey_Nova_20260328_194345.tflite"
_CHUNK_SAMPLES = 1280   # 80ms at 16kHz
_THRESHOLD     = 0.5    # detection confidence threshold


class WakeWordListener:
    def __init__(
        self,
        on_detect: Callable[[], None],
        model_path: str = str(MODEL_PATH),
        threshold: float = _THRESHOLD,
    ) -> None:
        self._on_detect  = on_detect
        self._model_path = model_path
        self._threshold  = threshold
        self._model      = None
        self._stream: Optional[sd.InputStream] = None
        self._running    = False

    def start(self) -> None:
        self._model = _OWWModel(
            wakeword_models=[self._model_path],
            inference_framework="tflite",
        )
        self._running = True
        self._stream = sd.InputStream(
            samplerate=16_000,
            channels=1,
            dtype="int16",
            blocksize=_CHUNK_SAMPLES,
            callback=self._on_audio,
        )
        self._stream.start()

    def stop(self) -> None:
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._model = None

    def is_running(self) -> bool:
        return self._running

    def _on_audio(self, indata, frames, time, status) -> None:
        if not self._running or self._model is None:
            return
        audio = indata[:, 0]   # int16 mono array
        prediction = self._model.predict(audio)
        if any(v >= self._threshold for v in prediction.values()):
            self._on_detect()
