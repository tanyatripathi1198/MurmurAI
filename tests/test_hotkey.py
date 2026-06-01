import pytest
from unittest.mock import patch, MagicMock


def test_is_valid_space():
    from hotkey import HotkeyManager
    assert HotkeyManager.is_valid("ctrl+shift+space") is True


def test_is_valid_function_key():
    from hotkey import HotkeyManager
    assert HotkeyManager.is_valid("ctrl+f5") is True


def test_is_valid_letter():
    from hotkey import HotkeyManager
    assert HotkeyManager.is_valid("ctrl+shift+a") is True


def test_is_valid_unknown_key_returns_false():
    from hotkey import HotkeyManager
    assert HotkeyManager.is_valid("ctrl+shift+xyz_bad_key") is False


def test_register_starts_listener():
    with patch("hotkey._kb.GlobalHotKeys") as mock_gk:
        mock_instance = MagicMock()
        mock_gk.return_value = mock_instance
        from hotkey import HotkeyManager
        mgr = HotkeyManager()
        cb = MagicMock()
        mgr.register("ctrl+shift+space", cb)
    mock_gk.assert_called_once_with({"<ctrl>+<shift>+<space>": cb})
    mock_instance.start.assert_called_once()


def test_register_replaces_previous_listener():
    with patch("hotkey._kb.GlobalHotKeys") as mock_gk:
        mock_gk.return_value = MagicMock()
        from hotkey import HotkeyManager
        mgr = HotkeyManager()
        cb = MagicMock()
        mgr.register("ctrl+shift+space", cb)
        first = mock_gk.return_value
        mock_gk.return_value = MagicMock()
        mgr.register("ctrl+f1", cb)
    first.stop.assert_called_once()


def test_unregister_when_nothing_registered_does_not_raise():
    from hotkey import HotkeyManager
    HotkeyManager().unregister()


def test_to_pynput_conversion():
    from hotkey import _to_pynput
    assert _to_pynput("ctrl+shift+space") == "<ctrl>+<shift>+<space>"
    assert _to_pynput("ctrl+f1") == "<ctrl>+<f1>"
    assert _to_pynput("ctrl+alt+a") == "<ctrl>+<alt>+a"
