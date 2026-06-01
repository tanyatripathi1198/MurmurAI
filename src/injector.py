import ctypes
import time
import pyperclip
import pyautogui

pyautogui.PAUSE = 0


class TextInjector:
    def type_text(self, text: str) -> None:
        if not text.strip():
            return

        # Capture the currently focused window RIGHT NOW, before we do anything.
        # Transcription takes 2-5 seconds — the user may have clicked elsewhere by
        # the time this method is called, so we refocus the intended target explicitly.
        target = ctypes.windll.user32.GetForegroundWindow()

        original = ""
        try:
            original = pyperclip.paste()
        except Exception:
            pass

        try:
            pyperclip.copy(" " + text)
            time.sleep(0.1)     # let clipboard settle, especially on Electron apps

            # Restore focus so the paste lands in the right window
            if target:
                ctypes.windll.user32.SetForegroundWindow(target)
                time.sleep(0.05)

            # Release any modifier keys that pynput may have left in a "down" state
            for mod in ("ctrl", "shift", "alt"):
                pyautogui.keyUp(mod)

            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.15)    # let the target app process the paste
        finally:
            try:
                pyperclip.copy(original)
            except Exception:
                pass
