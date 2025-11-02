# Research: Voice-Enabled Character Interaction for Claude Code

**Date**: 2025-11-01
**Feature**: Voice-Enabled Character Interaction
**Phase**: 0 (Outline & Research)

## Overview

This document consolidates research findings for implementing voice interaction with character roleplay in Claude Code. Research focuses on resolving technical unknowns from the plan.md Technical Context section while adhering to YAGNI/KISS principles.

## Research Areas

### 1. Language/Runtime for Claude Code Hooks

**Question**: Should we use Node.js/TypeScript or Python for implementing Claude Code hooks?

**Decision**: **Python 3.11+**

**Rationale**:
- **Project requirement**: Python mandated as primary language
- **Rich AI/ML ecosystem**: Native integration with speech libraries (SpeechRecognition, pyttsx3, elevenlabs-python)
- **Audio processing**: Excellent libraries (PyAudio, sounddevice, pydub)
- **Web Speech API**: Can be accessed via browser automation (Selenium/Playwright) or system APIs
- **Cross-platform support**: Works seamlessly on Windows/macOS/Linux
- **Simplicity**: Direct integration with system TTS/STT without complex wrappers
- **ElevenLabs SDK**: Official Python SDK available (`elevenlabs` package)
- **Whisper**: OpenAI Whisper has excellent Python support (both API and local)

**Alternatives Considered**:
- **Node.js/TypeScript**: Better if Claude Code is TypeScript-based, but Python requirement overrides
- **Rust**: Best performance, but harder to integrate with AI services and overkill for this use case

**Implementation Impact**:
- Language/Version: **Python 3.11+**
- Testing framework: **pytest** with pytest-asyncio for async tests
- Package manager: **pip** with **requirements.txt** or **poetry**

---

### 2. Speech-to-Text Service Selection

**Question**: Which STT service supports Polish language, handles technical English terms, and meets <2s latency requirement?

**Decision**: **Web Speech API** (browser/system-based) with **OpenAI Whisper API** as fallback

**Rationale**:
- **Web Speech API** (Primary):
  - **Cost**: Free (uses browser's built-in or system STT)
  - **Polish language support**: Good support in Chrome/Edge (Google STT backend)
  - **Latency**: Very fast (<1s typically), processes locally or via browser's STT service
  - **Privacy**: Can work offline on some systems (Windows Speech Recognition, macOS Dictation)
  - **Integration**: Can be accessed from Node.js via Electron or headless browser (Puppeteer)
  - **Simplicity**: No API key required, uses system/browser capabilities

- **OpenAI Whisper API** (Fallback):
  - Used when Web Speech API unavailable or accuracy insufficient
  - Better accuracy for technical terms and mixed language
  - Requires API key and costs $0.006/minute

**Implementation Approach**:
1. Primary: Use Web Speech API via Electron (if available) or system speech recognition APIs
2. Fallback: OpenAI Whisper API if primary method fails or disabled by user
3. Configuration: User can choose preferred STT provider

**Alternatives Considered**:
- **Google Cloud Speech-to-Text**: Comparable to Whisper, but more complex auth
- **Azure Speech Services**: Good quality, but more expensive and complex SDK
- **Local Whisper (whisper.cpp)**: No API costs, but:
  - Requires local model download (~1-3GB)
  - Slower transcription on CPU (>2s for small model)
  - Adds complexity for model management

**Implementation Impact**:
- Primary Dependency: **Web Speech API** via system integration or Electron
- Secondary Dependency: **OpenAI Whisper API** via `openai` npm package (fallback)
- Cost: $0 for Web Speech API, ~$0.72/month for Whisper fallback (if used)
- Configuration option: Let user choose STT provider (Web Speech vs Whisper)

---

### 3. Text-to-Speech Service Selection

**Question**: Which TTS service supports Polish, enables character voice modulation, and meets <1s playback start?

**Decision**: **ElevenLabs API** as primary, with **System TTS** as automatic fallback

**Rationale**:
- **ElevenLabs API** (Primary - when API key provided):
  - **Polish language support**: Excellent multilingual support including Polish with natural pronunciation
  - **Character voices**: Can create custom voice models for specific characters (e.g., Toadwart with unique personality)
  - **Voice quality**: Industry-leading natural speech quality, far superior to standard TTS
  - **Character modulation**: Two-layer approach:
    - Text transformation: Apply character personality to response text
    - Voice cloning: Use ElevenLabs voice that matches character (or create custom voice)
  - **Latency**: Streaming audio with WebSocket API starts in ~500ms
  - **Emotional range**: Voice can convey emotion and energy (perfect for cheerful Toadwart character)

- **System TTS** (Automatic Fallback - when no ElevenLabs API key):
  - **Cost**: Free (uses OS built-in text-to-speech)
  - **Zero configuration**: Works out of the box, no API key needed
  - **Platform support**:
    - Windows: SAPI (System.Speech or Windows.Media.SpeechSynthesis)
    - macOS: `say` command (NSSpeechSynthesizer)
    - Linux: `espeak` or `festival`
  - **Polish support**: Available on most systems (quality varies by OS)
  - **Simplicity**: Single command/API call per platform
  - **Privacy**: 100% offline, no data sent to external services
  - **Character limitation**: Text transformation still applied, but voice quality lower and no custom voice cloning

**Implementation Strategy**:
1. Check if `apiKeys.elevenlabs` is configured
2. If YES: Use ElevenLabs API (premium experience)
3. If NO: Automatically use System TTS (free, basic experience)
4. No user intervention required - seamless fallback

**Alternatives Considered**:
- **OpenAI TTS API**: Good quality, affordable ($15/1M chars), but still requires API key and costs money
- **Google Cloud TTS**: More complex SDK, lower voice quality
- **Azure Speech Services**: SSML support, but complex setup and lower quality

**Character Implementation Approach**:
- **Text transformation**: Apply character personality through prompt-based text modification (same as before)
- **Voice selection**: Each character profile specifies ElevenLabs voice ID
  - Option 1: Use pre-made ElevenLabs voices (quickest)
  - Option 2: Create custom voice for character (better personalization, requires voice samples)
- Character profiles stored as JSON with:
  - `name`: Character identifier
  - `voiceId`: ElevenLabs voice ID (e.g., "21m00Tcm4TlvDq8ikWAM" for Rachel voice)
  - `systemPrompt`: Instructions for transforming response text
  - `phrases`: Array of characteristic expressions

**Example Toadwart Profile**:
```json
{
  "name": "Toadwart",
  "voiceId": "21m00Tcm4TlvDq8ikWAM",
  "voiceSettings": {
    "stability": 0.5,
    "similarityBoost": 0.75
  },
  "systemPrompt": "Transform responses to sound like Toadwart from Gummy Bears: cheerful, helpful, occasionally references Gummi Berry juice or adventures. Add personality but keep technical content intact.",
  "phrases": ["Great gobs of gummiberries!", "Bouncing bears!", "Let me check the Gummi archives..."]
}
```

**No plugin architecture needed**: Character transformation remains simple function. SOLID: Single responsibility maintained.

**Implementation Impact**:
- Primary Dependency: **ElevenLabs API** via `elevenlabs` npm package (when API key provided)
- Automatic Fallback: **System TTS** via platform-specific APIs (when no ElevenLabs key):
  - Windows: `edge-tts` npm package or Windows SAPI
  - macOS: `say` command via child_process
  - Linux: `espeak` or `festival` via child_process
- Cost consideration:
  - With ElevenLabs: $5-22/month depending on usage
  - Without ElevenLabs: $0/month (free system TTS)
- Character system: JSON profiles + transformation function (no separate plugin framework)
- User experience: Seamless - works immediately without any API keys (basic quality), upgrades automatically when ElevenLabs key added (premium quality)

---

### 4. Audio Handling Best Practices

**Question**: How to handle cross-platform audio input/output in Node.js?

**Decision**: Use `node-mic` for input and `speaker` for output with OS-level audio API fallbacks

**Rationale**:
- **node-mic**: Simple push-to-talk audio capture, works on Windows/Mac/Linux
- **speaker**: PCM audio playback, direct OS audio API access
- **Cross-platform**: Both packages use native OS audio APIs (PortAudio underneath)
- **Simplicity**: Minimal configuration, stream-based API

**Best Practices**:
- Detect audio device availability on startup
- Provide clear error messages if microphone/speaker unavailable
- Allow user to select audio devices in config
- Gracefully degrade: disable voice features if audio unavailable

**Alternatives Considered**:
- **node-record-lpcm16**: More features, but heavier and unnecessary complexity
- **naudiodon**: Professional audio library, overkill for simple capture/playback

**Implementation Impact**:
- Dependencies: `node-mic`, `speaker`, `@types/node-mic`, `@types/speaker`

---

### 5. Push-to-Talk Implementation

**Question**: How to implement cross-platform keyboard/mouse button monitoring for push-to-talk?

**Decision**: Use `iohook` for global hotkey detection

**Rationale**:
- **Cross-platform**: Works on Windows, macOS, Linux
- **Global hotkeys**: Detects key presses even when Claude Code window not focused
- **Low-level**: Direct OS-level event hooks
- **Configurable**: User can set custom push-to-talk key

**Best Practices**:
- Default hotkey: Ctrl+Space (less likely to conflict)
- Allow user to configure in settings
- Provide visual/audio feedback when hotkey active
- Release resources when voice mode disabled

**Alternatives Considered**:
- **robotjs**: More features (mouse control, etc.), but heavier and unnecessary
- **nut-js**: Modern alternative, but less mature ecosystem

**Implementation Impact**:
- Dependency: `iohook`
- Default push-to-talk key: `Ctrl+Space` (configurable)

---

## Technology Stack Summary

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- `SpeechRecognition` - Primary STT library (supports Web Speech API, Google Speech, Whisper)
- `pyttsx3` - Cross-platform system TTS (free, offline)
- `pynput` - Global hotkey detection for push-to-talk
- `PyAudio` or `sounddevice` - Audio input capture
- `playsound` or `sounddevice` - Audio output playback

**Optional Dependencies** (premium features/fallbacks):
- `elevenlabs` - ElevenLabs Python SDK for premium TTS with character voices
- `openai` - OpenAI Python SDK (includes Whisper API)
- `edge-tts` - Microsoft Edge TTS (async, better quality on Windows)
- `pydub` - Audio format conversion and processing

**Storage**: JSON configuration files
- `.claude/voice-config.json` - User preferences (project root)
- `src/character/profiles/*.json` - Character profile definitions

**Testing**: pytest with pytest-asyncio

**Target Platform**: Windows, macOS, Linux (cross-platform desktop)

---

## Architecture Principles Adherence

### YAGNI/KISS Compliance

✅ **Character roleplay**: Simple text transformation function, not plugin architecture
✅ **Audio handling**: Direct library usage, no abstraction layers
✅ **Configuration**: Plain JSON files, no database
✅ **STT/TTS**: Direct API calls, no service abstraction layer (single provider)

### SOLID Compliance

✅ **Single Responsibility**: Each module handles one concern (audio capture, STT, TTS, character transform, config)
✅ **Open/Closed**: Character profiles are data-driven (add new characters by adding JSON, no code changes)
✅ **Dependency Inversion**: STT/TTS services implement common interface (future provider swap possible without major refactor, though not needed now per YAGNI)

### No Speculative Features

✅ All technology choices directly support P1/P2/P3 user stories
✅ No "future-proofing" for multi-user, voice translation, or custom voice training
✅ Character system: Minimal implementation supporting required functionality

---

## Performance Validation

**Estimated Latencies** (based on research):
- Push-to-talk activation: <50ms (OS-level event handling)
- Audio capture: Real-time streaming
- Whisper API transcription: 0.5-2s (depending on audio length)
- Character text transformation: <10ms (simple string manipulation)
- OpenAI TTS response: 300-800ms to first audio chunk (streaming)
- Audio playback start: <100ms (direct speaker API)

**Total end-to-end latency** (speak → hear response):
- User speaks command (variable)
- Wait 2s max (STT) ✅ Meets SC-002
- Claude Code processes command (variable, out of scope)
- Transform response text <10ms
- TTS playback starts <1s ✅ Meets SC-003
- Interrupt response: <500ms (stop playback + clear buffer) ✅ Meets SC-006

All performance goals from plan.md are achievable with selected technologies.

---

## Cost Analysis

**API Usage** (estimated):

**Speech-to-Text**:
- Primary (Web Speech API): **$0/month** (free, system/browser-based)
- Fallback (OpenAI Whisper): **$0-0.72/month** (only if Web Speech fails and user provides API key)
  - Pricing: $0.006/minute
  - Typical fallback usage: ~4 minutes/month (if needed)

**Text-to-Speech**:

*Option 1: Completely Free (No API Keys)*
- System TTS: **$0/month** (uses OS built-in TTS)
- Quality: Basic but functional
- Character support: Text transformation only (personality in words, not voice)

*Option 2: Premium Quality (ElevenLabs API Key)*
- ElevenLabs pricing tiers:
  - Creator: $5/month for 30,000 chars
  - Independent Publisher: $22/month for 100,000 chars
- Typical usage: ~50 responses/day × 100 characters = 5,000 chars/day = 150,000 chars/month
- Recommended tier: **Independent Publisher ($22/month)** for regular daily use
- Alternative: Creator tier ($5/month) for lighter usage (~15 responses/day)

**Total monthly cost by configuration**:

| Configuration | STT | TTS | Total |
|---------------|-----|-----|-------|
| **Basic (no API keys)** | Web Speech (free) | System TTS (free) | **$0/month** ✅ |
| **Light usage (ElevenLabs)** | Web Speech (free) | ElevenLabs Creator | **$5/month** |
| **Regular usage (ElevenLabs)** | Web Speech (free) | ElevenLabs Indie | **$22/month** |
| **With Whisper fallback** | +Whisper | Any TTS | +$0-0.72/month |

**Key advantage**: Feature works out-of-the-box with $0/month cost. Users can optionally upgrade to premium quality by adding ElevenLabs API key.

---

## Risk Mitigation

**API Availability**:
- Risk: OpenAI API outage breaks voice features
- Mitigation: Degrade gracefully - show error message, allow text input fallback
- Future: Consider local Whisper fallback if API reliability becomes issue (YAGNI: don't implement now)

**Audio Device Issues**:
- Risk: Missing or disconnected microphone/speaker
- Mitigation: Detect on startup, provide clear error messages, allow device selection

**Polish Language Support**:
- Risk: STT/TTS accuracy lower for Polish than English
- Mitigation: Test with Polish commands during implementation, document any limitations
- Fallback: User can switch to English if Polish accuracy insufficient

**Character Personality vs Technical Accuracy**:
- Risk: Character transformation corrupts technical content
- Mitigation: Transform only non-technical portions (greetings, confirmations), preserve code snippets, file paths, error messages verbatim
- Testing: Verify SC-004 (100% technical accuracy maintained)

---

## Open Questions for Phase 1

None. All technical unknowns resolved. Ready to proceed to Phase 1 (Design & Contracts).
