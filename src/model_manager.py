import os
from pathlib import Path
from typing import Optional, Type

MODEL_NAME = "small"
MODEL_DIR = Path(os.environ.get("APPDATA", Path.home())) / "MurmurAI" / "models"
_MARKER = MODEL_DIR / ".model_ready"


def is_ready() -> bool:
    return _MARKER.exists()


def ensure_model(_whisper_cls: Optional[Type] = None) -> None:
    """Download Whisper model if not present. _whisper_cls is injected in tests."""
    if is_ready():
        return
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if _whisper_cls is None:
        from faster_whisper import WhisperModel
        _whisper_cls = WhisperModel
    _whisper_cls(
        MODEL_NAME,
        device="cpu",
        compute_type="int8",
        download_root=str(MODEL_DIR),
    )
    _MARKER.touch()
