# Novaa AI — Design Spec
**Date:** 2026-05-31  
**Status:** Approved

---
## Overview

Novaa AI is a Windows desktop app that transcribes speech in real-time and types the result directly into whatever window is currently focused. It runs as a system-tray app with a small card UI, activated via a customizable global hotkey or an on-screen button. All transcription runs locally using OpenAI's Whisper model — no internet or API key required.

---

## Core User Flow

1. User presses hotkey (or clicks mic button) — recording starts
2. As the user speaks, audio is transcribed in ~1s chunks and typed into the active window in real-time
3. User presses hotkey again — recording stops, any remaining audio is flushed and typed
4. App returns to idle state

---

## Architecture

Single Python process with four logical layers:

```
┌─────────────────────────────────────────────┐
│  UI Layer (CustomTkinter)                   │
│  Small card window + system tray icon       │
├─────────────────────────────────────────────┤
│  Controller (main thread)                   │
│  Hotkey listener, state machine             │
│  (IDLE → RECORDING → TYPING → IDLE)        │
├─────────────────────────────────────────────┤
│  Audio + Transcription (background thread)  │
│  sounddevice → audio buffer → faster-whisper│
├─────────────────────────────────────────────┤
│  Text Injection (Windows API)               │
│  pywin32 SendInput → active window          │
└─────────────────────────────────────────────┘
```

- The **hotkey listener** runs in a daemon thread via the `keyboard` library and sends toggle events to the controller via a thread-safe queue
- The **controller** owns the state machine and coordinates layers; state drives UI updates
- **Transcription** runs in its own thread — audio captured in ~1s chunks, each transcribed and injected immediately
- **Text injection** uses `pywin32 SendInput` — works in all apps, does not touch the clipboard

---

## UI/UX

### Window
- Small card window (~240px wide), centered on screen by default, remembers last position
- Dark theme, always-on-top when recording
- Hides to system tray on close; re-summoned by clicking the tray icon
- **Hotkey works while window is hidden** — pressing the hotkey starts recording without summoning the window; the tray icon changes color to signal state. This is intentional so the user isn't interrupted mid-task.

### States

| State | Mic Button | Label | Glow |
|---|---|---|---|
| Idle | Grey mic 🎙 | "Press to record" | None |
| Recording | Red mic 🎙 | "Recording..." | Red pulse |
| Typing | Blue keyboard ⌨️ | "Typing..." | Blue pulse |

### Settings Panel
- Accessed via ⚙ icon at bottom of card — flips the card in-place (no separate window)
- **Hotkey field:** click-to-capture — user clicks field and presses their desired combo
- **Language dropdown:** defaults to "Auto-detect"; scrollable list of all Whisper-supported languages (~100)
- **Start on login toggle:** registers/removes Windows startup entry
- Save button persists to `%APPDATA%\NovaaAI\settings.json`

### System Tray
- Tray icon mirrors recording state color (grey/red/blue)
- Right-click menu: Open, Settings, Quit

---

## Audio + Transcription Pipeline

```
Microphone
  → sounddevice (continuous stream, 16kHz mono float32)
  → Audio buffer (accumulates ~1s of audio)
  → faster-whisper (small model, int8 quantized)
  → Text queue (thread-safe)
  → pywin32 SendInput
  → Active window
```

### Key Decisions
- **Model loads at startup** (not on first hotkey press) to avoid a cold-start delay
- **Chunk size: ~1000ms** — balances real-time feel with Whisper accuracy; shorter chunks cause hallucinations
- **VAD enabled** (faster-whisper built-in) — silent chunks are skipped, no phantom text injected on pauses
- **Language handling:** if set to auto-detect, faster-whisper infers from first chunk; if explicit, detection is skipped for speed
- **Whisper model:** `small` (~500MB, int8 quantized via faster-whisper for ~2× speed boost)

---

## Text Injection

- Uses `pywin32` `SendInput` with virtual key codes
- Works in all Windows applications including browsers, IDEs, Office apps
- Does **not** touch the clipboard (no paste artifacts)
- Special characters and unicode handled via `VK_PACKET` input type

---

## Hotkey System

- Global hotkey registered via the `keyboard` library (works system-wide, even when app window is hidden)
- Default: `Ctrl+Shift+Space`
- User-customizable via settings panel (click-to-capture)
- Hotkey stored in `settings.json`; re-registered on each app start
- Conflict detection: warns if the chosen combo is already registered by another app

---

## Language Support

- Whisper `small` model supports ~100 languages
- Default: **Auto-detect** (faster-whisper infers language from audio)
- User can pin a specific language in settings for slightly faster transcription
- Language setting persisted in `settings.json`

---

## First-Run Experience

1. App launches → checks for model files in `%APPDATA%\NovaaAI\models\`
2. If not found: progress bar replaces mic button during download (~500MB); app is non-functional until complete
3. After download: hotkey setup prompt (confirm default or set custom)
4. Ready — user lands on idle card

---

## Error Handling

| Scenario | Behavior |
|---|---|
| No microphone detected | Error message in card on startup; links to Windows Sound Settings |
| Model download fails | Retry button shown; error logged |
| Silent audio chunk | VAD skips it; nothing injected |
| Target window loses focus mid-dictation | Text injects into newly focused window (by design) |
| Unhandled exception | Logged to `%APPDATA%\NovaaAI\logs\novaaai.log`; tray icon turns grey |

---

## Packaging & Distribution

- **Bundler:** PyInstaller → single `.exe`, no Python install required
- **Model files:** downloaded at first run (not bundled, too large)
- **Settings:** `%APPDATA%\NovaaAI\settings.json`
- **Logs:** `%APPDATA%\NovaaAI\logs\novaaai.log`
- **Start on login:** Windows registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (optional, toggled in settings)

---

## Dependencies

| Package | Purpose |
|---|---|
| `faster-whisper` | Local speech-to-text (wraps CTranslate2 + Whisper) |
| `sounddevice` | Microphone audio capture |
| `numpy` | Audio buffer manipulation |
| `customtkinter` | Modern dark-theme UI |
| `keyboard` | Global hotkey registration |
| `pywin32` | Windows text injection (SendInput) + tray icon |
| `pystray` | System tray icon management |
| `PyInstaller` | Packaging to `.exe` |

---

## Out of Scope

- macOS / Linux support
- Wake-word activation (e.g. "Hey Nova")
- Punctuation commands (e.g. "comma", "new line")
- Cloud transcription fallback
- Multi-microphone selection (uses system default)
