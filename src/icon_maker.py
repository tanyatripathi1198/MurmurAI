import os
from pathlib import Path
from PIL import Image, ImageDraw

APPDATA = Path(os.environ.get("APPDATA", Path.home())) / "NovaaAI"
ICO_PATH = APPDATA / "novaaai.ico"


def _draw_n(draw, size, color=(255, 255, 255, 210), lw=None):
    """Draw the letter N using lines, scaled to size."""
    if lw is None:
        lw = max(1, size // 13)
    top = int(size * 0.19)
    bottom = int(size * 0.81)
    left = int(size * 0.23)
    right = int(size * 0.77)
    draw.line([(left, top), (left, bottom)], fill=color, width=lw)
    draw.line([(right, top), (right, bottom)], fill=color, width=lw)
    draw.line([(left, top), (right, bottom)], fill=color, width=lw)


def make_icon_image(size: int, bg: tuple = (11, 11, 15, 255)) -> Image.Image:
    """Create a single-size icon: rounded dark square with white N."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = max(2, size // 6)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=bg)
    _draw_n(draw, size)
    return img


def ensure_icon() -> str:
    """Generate and cache novaaai.ico. Returns path string."""
    APPDATA.mkdir(parents=True, exist_ok=True)
    if not ICO_PATH.exists():
        sizes = [16, 32, 48, 64, 128, 256]
        images = [make_icon_image(s) for s in sizes]
        images[0].save(
            str(ICO_PATH),
            format="ICO",
            sizes=[(s, s) for s in sizes],
            append_images=images[1:],
        )
    return str(ICO_PATH)
