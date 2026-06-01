import ctypes
import time
import pyperclip
import pyautogui

pyautogui.PAUSE = 0

# Window title fragments that indicate a terminal is focused.
# VS Code terminal shows the shell name in the title, e.g.:
#   "PowerShell - project - Visual Studio Code"
#   "bash - project - Visual Studio Code"
#   "Windows PowerShell"  (standalone Windows Terminal)
_TERMINAL_TITLES = (
    "powershell", "bash", "cmd", "command prompt",
    "wsl", "terminal", "zsh", "fish", "sh -",
)


def _foreground_title() -> str:
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    n = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    if n == 0:
        return ""
    buf = ctypes.create_unicode_buffer(n + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value.lower()


def _is_terminal() -> bool:
    title = _foreground_title()
    return any(kw in title for kw in _TERMINAL_TITLES)


class TextInjector:
    def type_text(self, text: str) -> None:
        if not text.strip():
            return
        original = ""
        try:
            original = pyperclip.paste()
        except Exception:
            pass
        try:
            pyperclip.copy(" " + text)
            time.sleep(0.05)
            if _is_terminal():
                pyautogui.hotkey("ctrl", "shift", "v")  # terminal paste
            else:
                pyautogui.hotkey("ctrl", "v")           # editor / browser paste
            time.sleep(0.1)
        finally:
            try:
                pyperclip.copy(original)
            except Exception:
                pass
