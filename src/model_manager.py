import os
from pathlib import Path
from typing import Optional, Type

MODEL_NAME = "small"
MODEL_DIR = Path(os.environ.get("APPDATA", Path.home())) / "Pooky" / "models"
_MARKER = MODEL_DIR / ".model_ready"


def is_ready() -> bool:
    if not _MARKER.exists():
        return False
    # Guard against stale markers (e.g. created by test mocks without real files)
    return any(MODEL_DIR.rglob("*.bin"))


def _patch_ssl() -> None:
    """Bypass corporate proxy SSL cert issues for the HuggingFace download."""
    import ssl
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except Exception:
        pass
    try:
        import httpx
        from huggingface_hub.utils._http import set_client_factory
        set_client_factory(lambda: httpx.Client(verify=False))
    except Exception:
        pass


def ensure_model(_whisper_cls: Optional[Type] = None) -> None:
    """Download Whisper model if not present. _whisper_cls is injected in tests."""
    if is_ready():
        return
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if _whisper_cls is None:
        _patch_ssl()
        from faster_whisper import WhisperModel
        _whisper_cls = WhisperModel
    _whisper_cls(
        MODEL_NAME,
        device="cpu",
        compute_type="int8",
        download_root=str(MODEL_DIR),
    )
    _MARKER.touch()
