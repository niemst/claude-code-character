# Implementation Plan: Voice-Enabled Character Interaction for Claude Code

**Branch**: `001-voice-character-interaction` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-voice-character-interaction/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable Claude Code to interact with users through voice commands and voice responses, with optional character roleplay (e.g., Toadwart from Gummy Bears) applied to spoken output only. The feature works out-of-the-box using free system services (Web Speech API for STT, system TTS) with optional premium upgrade to ElevenLabs for superior voice quality. Uses push-to-talk activation for voice input, converts speech to text for command execution, and converts Claude Code responses to speech output with character personality overlay while maintaining 100% technical accuracy in actual work execution.

**Key Feature**: Zero-configuration experience - no API keys required for basic functionality. Users can optionally add ElevenLabs API key to upgrade voice quality.

## Technical Context

**Language/Version**: Python 3.11+ (project requirement)
**Primary Dependencies**: `SpeechRecognition` (STT with multiple backends), `pyttsx3` (system TTS), `elevenlabs` (premium TTS), `pynput` (global hotkey for push-to-talk), `PyAudio`/`sounddevice` (audio I/O), Optional: `openai` (Whisper API as STT fallback)
**Storage**: JSON configuration files (`.claude/voice-config.json` in project root for user preferences, `src/character/profiles/*.json` for character definitions)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Windows, macOS, Linux (cross-platform desktop environment where Claude Code runs)
**Project Type**: Single project (CLI extension/hook system for Claude Code)
**Performance Goals**:
  - Speech-to-text conversion: <2 seconds from end of speech
  - Text-to-speech playback start: <1 second from response ready
  - Push-to-talk interrupt response: <500ms
  - Voice toggle activation: <3 seconds
**Constraints**:
  - Must work with Claude Code's existing hook system
  - Must support Polish language and mixed Polish/English technical terminology
  - Must handle audio device availability gracefully
  - Character roleplay must NOT affect code execution quality
**Scale/Scope**: Single-user desktop application, processing one voice command at a time, supporting multiple character profiles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity & Code Quality

**Status**: ✅ PASS (Post-Phase 1 Re-evaluation)

**Analysis**:
- ✅ Feature requires minimal abstractions: audio capture → STT → command execution → TTS with character overlay
- ✅ No speculative features: All requirements directly support defined user stories
- ✅ **Character roleplay resolved**: Research confirmed simple text transformation function (no plugin architecture) - YAGNI compliant
- ✅ SOLID principles applied in design: Single responsibility for each module (audio, voice, character, config)
- ✅ Standard Python libraries used: `SpeechRecognition`, `pyttsx3`, `PyAudio` - minimal dependencies
- ✅ Zero-configuration approach: System TTS/STT fallbacks ensure feature works without any setup

**Resolution**: Phase 0 research confirmed simplest implementation. Character system uses JSON profiles + transformation function. No unnecessary abstractions identified.

### Principle II: Language & Communication Policy

**Status**: ✅ PASS (Post-Phase 1 Re-evaluation)

**Analysis**:
- ✅ All documentation in English (spec.md, plan.md, research.md, data-model.md, quickstart.md completed)
- ✅ AI responses to user in Polish (voice output supports Polish language)
- ✅ Code identifiers, functions, variables in English
- ✅ Commit messages in English without AI attribution
- ✅ **Python requirement**: All code will be Python 3.11+ (project requirement met)
- ✅ Python naming conventions: snake_case for functions/variables, PascalCase for classes
- ✅ PEP 8 style guide and type hints (PEP 484) to be enforced

### Principle III: Incremental Delivery

**Status**: ✅ PASS

**Analysis**:
- ✅ User stories properly prioritized: P1 (voice input) → P2 (voice output) → P3 (character roleplay)
- ✅ Each story independently testable and deliverable
- ✅ P1 alone constitutes viable MVP (hands-free command input)
- ✅ Implementation can stop after each priority level with working feature

### Principle IV: Specification-First

**Status**: ✅ PASS

**Analysis**:
- ✅ Complete spec.md exists and approved
- ✅ User scenarios, acceptance criteria, success metrics defined
- ✅ Specification is technology-agnostic (no implementation details in spec)
- ✅ All clarifications resolved (push-to-talk method selected)

### Principle V: Independent Testability

**Status**: ✅ PASS

**Analysis**:
- ✅ User stories define independent acceptance scenarios
- ✅ Components can be tested in isolation:
  - Audio capture can be tested with mock microphone input
  - STT can be tested with recorded audio samples
  - TTS can be tested with text input
  - Character overlay can be tested with sample responses
- ✅ External dependencies (STT/TTS services) can be mocked for testing

### Principle VI: Documentation Completeness

**Status**: ✅ PASS (Post-Phase 1 Re-evaluation)

**Analysis**:
- ✅ spec.md complete (approved, no clarifications remaining)
- ✅ plan.md complete (this file, with resolved Technical Context)
- ✅ research.md complete (all technical decisions documented with rationale)
- ✅ data-model.md complete (VoiceConfiguration, CharacterProfile, VoiceSession fully specified)
- ✅ quickstart.md complete (comprehensive user guide with zero-config and premium setups)
- ✅ **All [NEEDS CLARIFICATION] markers resolved**: Language (Python 3.11+), STT (Web Speech + Whisper), TTS (System + ElevenLabs)
- ✅ Cross-artifact consistency maintained

**Resolution**: Phase 1 documentation is complete and ready for `/speckit.tasks` generation.

### Quality Standards

**Status**: ✅ PASS (Post-Phase 1 Re-evaluation)

**Testing Requirements**:
- Tests NOT explicitly requested in spec → tests are OPTIONAL
- pytest framework selected for Python testing (if needed)
- pytest-asyncio for async voice processing tests

**Code Quality**:
- ✅ SOLID, Clean Code, DRY, KISS principles designed into architecture
- ✅ Python tooling selected: `black` (formatting), `ruff` (linting), `mypy` (type checking)
- ✅ No comments policy enforced (self-documenting code with type hints)
- ✅ PEP 8 compliance required

**Complexity Justification**:
- ✅ No violations identified
- ✅ All design decisions documented in research.md with rationale
- ✅ Zero unnecessary abstractions (YAGNI enforced)

### Overall Gate Status

**✅ FULL PASS**: Phase 1 (Design & Contracts) complete. All conditions met:
1. ✅ All [NEEDS CLARIFICATION] markers resolved in Technical Context
2. ✅ Character roleplay follows YAGNI (simple text transformation, no plugin system)
3. ✅ Constitution Check re-evaluation complete (all principles pass)
4. ✅ Python 3.11+ requirement incorporated into constitution and design

**Ready for**: `/speckit.tasks` command to generate tasks.md for Phase 2 (Implementation)

## Project Structure

### Documentation (this feature)

```text
specs/001-voice-character-interaction/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── audio/
│   ├── __init__.py
│   ├── capture.py          # Audio input capture (push-to-talk)
│   ├── playback.py         # Audio output playback
│   └── device_manager.py   # Audio device enumeration/selection
├── voice/
│   ├── __init__.py
│   ├── speech_to_text.py   # STT service integration
│   ├── text_to_speech.py   # TTS service integration
│   └── voice_session.py    # Voice session state management
├── character/
│   ├── __init__.py
│   ├── profile.py          # Character profile definitions
│   ├── transformer.py      # Apply character personality to text
│   └── profiles/           # Character profile data files
│       └── toadwart.json     # Toadwart character profile
├── config/
│   ├── __init__.py
│   ├── voice_config.py     # Voice configuration management
│   └── persistence.py      # Save/load user preferences
├── hooks/
│   ├── __init__.py
│   ├── input_hook.py       # Claude Code input stream hook
│   └── output_hook.py      # Claude Code output stream hook
└── __main__.py             # Main entry point / hook registration

tests/
├── __init__.py
├── contract/               # API contract tests for STT/TTS services
│   └── __init__.py
├── integration/            # End-to-end voice flow tests
│   └── __init__.py
└── unit/                   # Unit tests for individual components
    └── __init__.py
```

**Structure Decision**: Single project structure selected because this is a Claude Code extension/hook system. All voice processing, character roleplay, and configuration management are part of one cohesive feature. No separate frontend/backend needed—this integrates directly with Claude Code's existing CLI interface through hooks.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations requiring justification at this stage. Will update if Phase 0 research identifies necessary complexity.*
