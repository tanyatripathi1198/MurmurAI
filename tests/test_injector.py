import pytest
from unittest.mock import patch, MagicMock


def _run_inject(text, window_title="Notepad"):
    with patch("injector.pyperclip") as mock_clip, \
         patch("injector.pyautogui") as mock_gui, \
         patch("injector.time"), \
         patch("injector._foreground_title", return_value=window_title.lower()):
        mock_clip.paste.return_value = "original"
        from injector import TextInjector
        TextInjector().type_text(text)
    return mock_clip, mock_gui


def test_editor_uses_ctrl_v():
    _, mock_gui = _run_inject("hello", "main.py - project - Visual Studio Code")
    mock_gui.hotkey.assert_called_once_with("ctrl", "v")


def test_terminal_uses_ctrl_shift_v():
    _, mock_gui = _run_inject("hello", "PowerShell - project - Visual Studio Code")
    mock_gui.hotkey.assert_called_once_with("ctrl", "shift", "v")


def test_standalone_terminal_uses_ctrl_shift_v():
    _, mock_gui = _run_inject("hello", "Windows PowerShell")
    mock_gui.hotkey.assert_called_once_with("ctrl", "shift", "v")


def test_browser_uses_ctrl_v():
    _, mock_gui = _run_inject("hello", "Google Chrome")
    mock_gui.hotkey.assert_called_once_with("ctrl", "v")


def test_copies_to_clipboard_with_leading_space():
    mock_clip, _ = _run_inject("hello")
    mock_clip.copy.assert_any_call(" hello")


def test_restores_clipboard_after_paste():
    mock_clip, _ = _run_inject("hello")
    last_copy = mock_clip.copy.call_args_list[-1]
    assert last_copy.args[0] == "original"


def test_empty_text_makes_no_calls():
    _, mock_gui = _run_inject("")
    mock_gui.hotkey.assert_not_called()
