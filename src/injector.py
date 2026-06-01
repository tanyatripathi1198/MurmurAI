import threading
import time
import pyperclip
import pyautogui

pyautogui.PAUSE = 0


class TextInjector:
    def type_text(self, text: str) -> None:
        if not text.strip():
            return
        original = ""
        try:
            original = pyperclip.paste()
        except Exception:
            pass

        pyperclip.copy(" " + text)          # clipboard write is synchronous — no sleep needed
        pyautogui.hotkey("shift", "insert")  # universal paste (works in editor + terminal)

        # Restore clipboard in background so we don't block the caller
        _orig = original
        threading.Thread(
            target=lambda: (time.sleep(0.3), pyperclip.copy(_orig)),
            daemon=True,
        ).start()
