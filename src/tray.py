import os
from pathlib import Path
import threading
from typing import Callable
import pystray
from PIL import Image, ImageDraw

_BG = {
    "idle":      (28, 28, 36),
    "recording": (48, 18, 24),
    "typing":    (16, 24, 40),
}
_FG = {
    "idle":      (200, 200, 200, 180),
    "recording": (255, 100, 120, 220),
    "typing":    (100, 160, 255, 220),
}


def _make_icon_image(state: str = "idle") -> Image.Image:
    size = 64
    bg = _BG.get(state, _BG["idle"])
    fg = _FG.get(state, _FG["idle"])
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=10, fill=(*bg, 255))
    # Draw N
    lw = 5
    top, bottom, left, right = 14, 50, 16, 48
    draw.line([(left, top), (left, bottom)], fill=fg, width=lw)
    draw.line([(right, top), (right, bottom)], fill=fg, width=lw)
    draw.line([(left, top), (right, bottom)], fill=fg, width=lw)
    return img


class TrayIcon:
    def __init__(self, on_open: Callable, on_quit: Callable) -> None:
        self._icon = pystray.Icon(
            "Novaa AI",
            _make_icon_image("idle"),
            "Novaa AI",
            menu=pystray.Menu(
                pystray.MenuItem("Open", lambda icon, item: on_open(), default=True),
                pystray.MenuItem("Quit", lambda icon, item: on_quit()),
            ),
        )

    def start(self) -> None:
        threading.Thread(target=self._icon.run, daemon=True).start()

    def set_state(self, state_name: str) -> None:
        self._icon.icon = _make_icon_image(state_name)

    def stop(self) -> None:
        self._icon.stop()
