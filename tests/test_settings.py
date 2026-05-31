import json
import pytest
from pathlib import Path
from unittest.mock import patch


def test_load_returns_defaults_when_no_file(tmp_path):
    with patch("settings.SETTINGS_PATH", tmp_path / "s.json"), \
         patch("settings.APPDATA_DIR", tmp_path):
        import importlib, settings
        s = settings.load()
    assert s.hotkey == "ctrl+shift+space"
    assert s.language == "auto"
    assert s.start_on_login is False


def test_save_and_load_roundtrip(tmp_path):
    with patch("settings.SETTINGS_PATH", tmp_path / "s.json"), \
         patch("settings.APPDATA_DIR", tmp_path):
        import importlib, settings
        orig = settings.Settings(hotkey="ctrl+f1", language="en", start_on_login=True)
        settings.save(orig)
        loaded = settings.load()
    assert loaded.hotkey == "ctrl+f1"
    assert loaded.language == "en"
    assert loaded.start_on_login is True


def test_load_ignores_unknown_keys(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"hotkey": "ctrl+f2", "unknown_key": "oops"}))
    with patch("settings.SETTINGS_PATH", p):
        import importlib, settings
        s = settings.load()
    assert s.hotkey == "ctrl+f2"


def test_load_returns_defaults_on_corrupt_json(tmp_path):
    p = tmp_path / "s.json"
    p.write_text("{{not json}}")
    with patch("settings.SETTINGS_PATH", p):
        import importlib, settings
        s = settings.load()
    assert s.hotkey == "ctrl+shift+space"
