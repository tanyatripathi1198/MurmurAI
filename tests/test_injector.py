import time
import pytest
from unittest.mock import patch, MagicMock


def test_type_text_copies_and_pastes():
    with patch("injector.pyperclip") as mock_clip, \
         patch("injector.pyautogui") as mock_gui, \
         patch("injector.threading"):
        mock_clip.paste.return_value = "original"
        from injector import TextInjector
        TextInjector().type_text("hello")
    mock_clip.copy.assert_called_once_with(" hello")
    mock_gui.hotkey.assert_called_once_with("shift", "insert")


def test_type_text_schedules_clipboard_restore():
    threads_started = []
    with patch("injector.pyperclip") as mock_clip, \
         patch("injector.pyautogui"), \
         patch("injector.threading") as mock_th:
        mock_clip.paste.return_value = "saved"
        mock_th.Thread.side_effect = lambda target, daemon: MagicMock(start=lambda: threads_started.append(target))
        from injector import TextInjector
        TextInjector().type_text("hello")
    # A background thread should be created to restore clipboard
    mock_th.Thread.assert_called_once()


def test_type_text_empty_makes_no_calls():
    with patch("injector.pyperclip") as mock_clip, \
         patch("injector.pyautogui") as mock_gui, \
         patch("injector.threading"):
        from injector import TextInjector
        TextInjector().type_text("")
    mock_gui.hotkey.assert_not_called()
    mock_clip.copy.assert_not_called()


def test_type_text_adds_leading_space():
    with patch("injector.pyperclip") as mock_clip, \
         patch("injector.pyautogui"), \
         patch("injector.threading"):
        mock_clip.paste.return_value = ""
        from injector import TextInjector
        TextInjector().type_text("world")
    assert mock_clip.copy.call_args.args[0] == " world"
