import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import model_manager


def test_is_ready_false_when_marker_missing(tmp_path):
    marker = tmp_path / ".ready"
    with patch.object(model_manager, "_MARKER", marker):
        assert not model_manager.is_ready()


def test_is_ready_true_when_marker_and_bin_exist(tmp_path):
    marker = tmp_path / ".ready"
    marker.touch()
    (tmp_path / "model.bin").write_bytes(b"fake")   # simulate real model file
    with patch.object(model_manager, "_MARKER", marker), \
         patch.object(model_manager, "MODEL_DIR", tmp_path):
        assert model_manager.is_ready()


def test_ensure_model_skips_when_ready(tmp_path):
    marker = tmp_path / ".ready"
    marker.touch()
    (tmp_path / "model.bin").write_bytes(b"fake")   # simulate real model file
    mock_cls = MagicMock()
    with patch.object(model_manager, "_MARKER", marker), \
         patch.object(model_manager, "MODEL_DIR", tmp_path):
        model_manager.ensure_model(_whisper_cls=mock_cls)
    mock_cls.assert_not_called()


def test_ensure_model_calls_whisper_and_writes_marker(tmp_path):
    marker = tmp_path / ".ready"
    mock_cls = MagicMock()
    with patch.object(model_manager, "_MARKER", marker), \
         patch.object(model_manager, "MODEL_DIR", tmp_path):
        model_manager.ensure_model(_whisper_cls=mock_cls)
    mock_cls.assert_called_once()
    assert marker.exists()
