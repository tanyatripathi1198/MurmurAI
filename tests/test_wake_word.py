import numpy as np
import pytest
from unittest.mock import patch, MagicMock


def _make_listener(on_detect=None):
    on_detect = on_detect or (lambda: None)
    with patch("wake_word._OWWModel") as mock_cls, \
         patch("wake_word.sd") as mock_sd:
        mock_model = MagicMock()
        mock_model.predict.return_value = {"hey_pooky": 0.0}
        mock_cls.return_value = mock_model
        mock_sd.InputStream.return_value = MagicMock()
        from wake_word import WakeWordListener
        listener = WakeWordListener(on_detect=on_detect, model_path="fake.tflite")
        listener.start()
        cb = mock_sd.InputStream.call_args.kwargs["callback"]
    return listener, mock_model, cb


def test_start_creates_model_and_stream():
    with patch("wake_word._OWWModel") as mock_cls, \
         patch("wake_word.sd") as mock_sd:
        mock_cls.return_value = MagicMock()
        mock_sd.InputStream.return_value = MagicMock()
        from wake_word import WakeWordListener
        WakeWordListener(on_detect=lambda: None, model_path="fake.tflite").start()
    mock_cls.assert_called_once_with(
        wakeword_models=["fake.tflite"], inference_framework="tflite"
    )
    mock_sd.InputStream.assert_called_once()


def test_is_running_after_start():
    listener, _, _ = _make_listener()
    assert listener.is_running() is True


def test_stop_cleans_up():
    with patch("wake_word._OWWModel") as mock_cls, \
         patch("wake_word.sd") as mock_sd:
        mock_cls.return_value = MagicMock()
        mock_stream = MagicMock()
        mock_sd.InputStream.return_value = mock_stream
        from wake_word import WakeWordListener
        listener = WakeWordListener(on_detect=lambda: None, model_path="fake.tflite")
        listener.start()
        listener.stop()
    mock_stream.stop.assert_called_once()
    mock_stream.close.assert_called_once()
    assert listener.is_running() is False


def test_detection_fires_callback():
    detections = []
    listener, mock_model, cb = _make_listener(on_detect=lambda: detections.append(1))
    mock_model.predict.return_value = {"hey_pooky": 0.9}   # above threshold
    cb(np.zeros((_CHUNK_SAMPLES := 1280, 1), dtype=np.int16), None, None, None)
    assert len(detections) == 1


def test_no_detection_below_threshold():
    detections = []
    listener, mock_model, cb = _make_listener(on_detect=lambda: detections.append(1))
    mock_model.predict.return_value = {"hey_pooky": 0.1}   # below threshold
    cb(np.zeros((1280, 1), dtype=np.int16), None, None, None)
    assert len(detections) == 0
