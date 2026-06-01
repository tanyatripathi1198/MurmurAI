# MurmurAI — Wake Word ("Hey Murmur") Design Spec
**Date:** 2026-06-01
**Status:** Approved

---

## Overview

Add always-listening wake word detection to MurmurAI using Picovoice Porcupine. Saying "Hey Murmur" starts recording automatically without pressing the hotkey. Recording stops after 3 seconds of silence (vs 1 second for hotkey-triggered recording) to tolerate natural thinking pauses. Wake word is opt-in via a settings toggle.

---

## User Setup (one-time)

1. Sign up at `picovoice.ai` → copy the free access key from the console dashboard.
2. In the Porcupine console → Create Wake Word → type "Hey Murmur" → train → download `.ppn` file → place at `%APPDATA%\MurmurAI\hey_murmur.ppn`.
3. In MurmurAI settings → enable "Wake word" toggle → paste access key → Save.

---

## Architecture

```
WakeWordListener (background thread)
  └── own sounddevice stream (16kHz, int16, 512-sample frames)
  └── pvporcupine.process(frame) → fires on "Hey Murmur"
  └── on_detect() → controller.wake_start() [only if IDLE]

Controller
  └── wake_start()  → _begin_recording(silence_blocks=30)  [3s silence]
  └── toggle()      → _begin_recording(silence_blocks=10)  [1s silence, unchanged]

AudioCapture
  └── start(chunk_callback, silence_blocks=10)  — new optional param
      wake mode passes 30, hotkey mode passes 10
```

`WakeWordListener` runs its own microphone stream independently from `AudioCapture`. The two streams coexist — the wake word stream keeps running during recording but ignores detections while not IDLE.

---

## New File: `src/wake_word.py`

```
WakeWordListener(access_key, model_path, on_detect)
  start()       — opens mic stream, starts porcupine thread
  stop()        — closes stream, deletes porcupine handle (frees native memory)
  is_running()  — bool
```

- Opens `sounddevice.InputStream` at 16kHz, blocksize = `porcupine.frame_length` (512), dtype=int16
- Audio callback: float32 → int16 conversion → `porcupine.process(frame)`
- If `process()` returns `>= 0`: detection — calls `on_detect()`
- `on_detect` is guarded in `main.py`: only fires if `controller.state == State.IDLE`
- Model path defaults to `%APPDATA%\MurmurAI\hey_murmur.ppn`

---

## Changes to Existing Files

### `src/settings.py`
Add two fields to `Settings` dataclass:
- `wake_word_enabled: bool = False`
- `picovoice_key: str = ""`

### `src/audio.py`
`AudioCapture.start()` gains an optional parameter:
- `start(chunk_callback, silence_blocks=10)`
- Stores `silence_blocks` and uses it in `_on_audio` instead of the `_SILENCE_BLOCKS_TO_END` constant
- Default value `10` (1s) preserves existing hotkey behaviour

### `src/controller.py`
Add one new public method:
- `wake_start()` — calls `_begin_recording(silence_blocks=30)`; no-op if not IDLE

`_begin_recording()` accepts an optional `silence_blocks` parameter and passes it to `audio.start()`.

### `src/ui.py`
Settings panel gets two new fields (below language dropdown):
- `CTkSwitch` — "Wake word" (on/off); toggling shows/hides the key field
- `CTkEntry` — "Picovoice key" (only visible when switch is on)
- `_save_settings()` passes `wake_word_enabled` and `picovoice_key` to `on_settings_save`

`MurmurWindow.__init__` signature gains `wake_word_enabled: bool = False` and `picovoice_key: str = ""`.

### `src/main.py`
- On startup: if `settings.wake_word_enabled` and `settings.picovoice_key`: create and start `WakeWordListener`
- `on_detect` callback: `lambda: controller.wake_start() if controller.state == State.IDLE else None`
- On settings save: stop existing listener (if any), restart with new key/enabled state
- `handle_settings_save` gains `wake_word_enabled` and `picovoice_key` params

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| `.ppn` file not found | Settings shows red label: "Model file not found at %APPDATA%\MurmurAI\hey_murmur.ppn" |
| Invalid access key | Porcupine raises on `start()` → settings shows: "Invalid Picovoice access key" |
| `pvporcupine` not installed | Skip wake word on startup; settings panel shows: "Install pvporcupine to use this feature" |
| Wake word fires while recording | Ignored — `on_detect` checks `controller.state == State.IDLE` |
| Mic stream conflict (device busy) | `WakeWordListener.start()` catches exception, sets `is_running()` to False |

---

## Dependencies

Add to `requirements.txt`:
```
pvporcupine>=3.0.0
```

---

## Out of Scope

- Bundling the `.ppn` model file (user downloads it manually from Picovoice console)
- Multiple wake words
- Changing the wake word from settings (user retrains and replaces the file)
- Visual waveform during wake word listening
