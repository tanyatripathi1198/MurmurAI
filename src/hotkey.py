from __future__ import annotations
from typing import Callable, Optional
from pynput import keyboard as _kb

_SPECIAL = {
    "ctrl", "shift", "alt", "win", "space",
    *{f"f{i}" for i in range(1, 13)},
}


def _to_pynput(combo: str) -> str:
    """Convert 'ctrl+shift+space' to '<ctrl>+<shift>+<space>'."""
    parts = []
    for p in combo.lower().split("+"):
        p = p.strip()
        parts.append(f"<{p}>" if p in _SPECIAL else p)
    return "+".join(parts)


class HotkeyManager:
    def __init__(self) -> None:
        self._listener: Optional[_kb.GlobalHotKeys] = None
        self._current: Optional[str] = None

    def register(self, combo: str, callback: Callable[[], None]) -> None:
        self.unregister()
        pynput_combo = _to_pynput(combo)
        try:
            self._listener = _kb.GlobalHotKeys({pynput_combo: callback})
            self._listener.start()
            self._current = combo
        except Exception:
            self._listener = None

    def unregister(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._current = None

    @staticmethod
    def is_valid(combo: str) -> bool:
        try:
            _kb.HotKey.parse(_to_pynput(combo))
            return True
        except Exception:
            return False
