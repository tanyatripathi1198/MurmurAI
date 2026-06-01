import time
import pyperclip
import pyautogui

# Disable pyautogui's default 0.1s pause between every action
pyautogui.PAUSE = 0


class TextInjector:
    def type_text(self, text: str) -> None:
        if not text.strip():
            return
        # Save clipboard so we can restore it after paste
        original = ""
        try:
            original = pyperclip.paste()
        except Exception:
            pass
        try:
            # Leading space prevents new text from running into the previous word.
            # Matches the approach used by Yap and similar dictation tools.
            pyperclip.copy(" " + text)
            pyautogui.hotkey("shift", "insert")
            time.sleep(0.05)          # minimal wait for target app to process paste
        finally:
            try:
                pyperclip.copy(original)
            except Exception:
                pass
