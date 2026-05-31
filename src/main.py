import sys
import threading
import winreg
from pathlib import Path

import customtkinter as ctk

from settings import Settings, load as load_settings, save as save_settings
from model_manager import is_ready, ensure_model
from audio import AudioCapture
from transcriber import Transcriber
from injector import TextInjector
from hotkey import HotkeyManager
from controller import Controller, State
from tray import TrayIcon
from ui import MurmurWindow


def _set_start_on_login(enabled: bool) -> None:
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, "MurmurAI", 0, winreg.REG_SZ, sys.executable)
        else:
            try:
                winreg.DeleteValue(key, "MurmurAI")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except OSError:
        pass


def _show_download_screen() -> None:
    """Blocking download screen — runs before the main window."""
    root = ctk.CTk()
    root.title("MurmurAI — First Run")
    root.geometry("300x160")
    root.resizable(False, False)

    ctk.CTkLabel(root, text="Downloading Whisper model (~500 MB)…",
                 wraplength=260).pack(pady=30)
    bar = ctk.CTkProgressBar(root)
    bar.pack(fill="x", padx=30)
    bar.set(0)

    def _download():
        ensure_model()
        root.after(0, root.destroy)

    threading.Thread(target=_download, daemon=True).start()
    root.mainloop()


def main() -> None:
    if not is_ready():
        _show_download_screen()

    settings = load_settings()

    audio       = AudioCapture()
    transcriber = Transcriber(language=settings.language)
    injector    = TextInjector()
    hotkey_mgr  = HotkeyManager()

    transcriber.load()   # ~1-2s on first call; blocks here intentionally

    # controller is referenced by the lambda before assignment — that is fine
    # because the lambda is only called after controller is created below.
    controller: Controller  # forward declaration for type checkers

    def handle_settings_save(hotkey: str, language: str, start_on_login: bool) -> None:
        settings.hotkey        = hotkey
        settings.language      = language
        settings.start_on_login = start_on_login
        save_settings(settings)
        hotkey_mgr.register(hotkey, controller.toggle)
        transcriber.set_language(language)
        window.update_hotkey_hint(hotkey)
        window.update_language_display(language)
        _set_start_on_login(start_on_login)

    window = MurmurWindow(
        on_toggle=lambda: controller.toggle(),
        on_settings_save=handle_settings_save,
    )

    def on_state_change(state: State) -> None:
        window.after(0, lambda s=state: window.update_state(s))
        tray.set_state(state.value)

    controller = Controller(
        audio, transcriber, injector,
        on_state_change=on_state_change,
    )

    def quit_app() -> None:
        hotkey_mgr.unregister()
        tray.stop()
        window.after(0, window.destroy)

    tray = TrayIcon(
        on_open=lambda: window.after(0, window.deiconify),
        on_quit=quit_app,
    )
    tray.start()

    hotkey_mgr.register(settings.hotkey, controller.toggle)
    window.update_hotkey_hint(settings.hotkey)
    window.update_language_display(settings.language)

    window.mainloop()


if __name__ == "__main__":
    main()
