import threading
import winsound


def _beep(freq: int, duration: int) -> None:
    try:
        winsound.Beep(freq, duration)
    except Exception:
        pass


def play_start() -> None:
    """Two quick ascending beeps — recording started."""
    def _play():
        _beep(880, 80)
        _beep(1100, 100)
    threading.Thread(target=_play, daemon=True).start()


def play_stop() -> None:
    """Single descending beep — recording stopped."""
    threading.Thread(target=lambda: _beep(550, 150), daemon=True).start()
