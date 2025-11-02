# Implementation Plan: Claude Code Voice Hooks Integration

**Branch**: `001-claude-voice-hooks` | **Date**: 2025-11-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-claude-voice-hooks/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate voice interaction system as Claude Code hooks. Stop hook captures Claude's text responses, transforms them through character profiles, and synthesizes speech using ElevenLabs TTS with streaming playback. Voice input daemon (optional P3) enables hands-free command input via OpenAI Whisper transcription. Core focus: seamless voice output integration that preserves Claude Code workflow while adding character personality.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: OpenAI Whisper, ElevenLabs TTS SDK, existing voice/character modules (src/voice, src/character, src/audio)
**Storage**: JSON configuration files (character profiles, voice config), JSONL transcript files (read-only from Claude Code)
**Testing**: pytest (existing test framework)
**Target Platform**: Windows/Linux desktop (Claude Code CLI environment)
**Project Type**: Single project (CLI integration via hooks)
**Performance Goals**: <5 seconds audio response latency, streaming TTS for messages >100 chars
**Constraints**: Hook timeout 30 seconds (Claude Code limit), non-blocking audio playback, preserve technical accuracy in character transformation
**Scale/Scope**: Single user local execution, process 50-5000 char responses, handle concurrent hook invocations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity & Code Quality

**Status**: ✅ PASS

- Reuses existing modules (src/voice, src/character, src/audio) - no duplication
- Hook script is simple: read transcript → transform → synthesize → play
- No speculative abstractions - direct implementation with existing components
- SOLID: Stop hook has single responsibility (voice output), character transformer separated
- DRY: Leverages existing TTS/character/audio infrastructure
- Clean Code: Hook script <150 lines, focused function responsibilities

### Principle II: Language & Communication Policy

**Status**: ✅ PASS

- Python 3.11+ (per Technical Context)
- All code, docs, artifacts in English
- Hook scripts follow Python conventions (snake_case, PEP 8)

### Coding Agent Instructions

**Status**: ✅ PASS

- Will use logging module (no print statements except CLI entry)
- No emojis in code/commits/docs
- Exception logging with exc_info=True for stack traces
- Commit messages in English, imperative mood

### Principle III: Incremental Delivery

**Status**: ✅ PASS

- P1 (Stop hook): Standalone MVP - voice output works independently
- P2 (Character quality): Enhancement to P1 - improves transformation without blocking P1
- P3 (Voice input daemon): Optional - P1 + P2 deliver full value without it
- Each story independently deliverable and testable

### Principle IV: Specification-First

**Status**: ✅ PASS

- Complete spec.md before planning (current phase)
- Technology-agnostic specification focused on WHAT and WHY
- Acceptance criteria defined for each user story

### Principle V: Independent Testability

**Status**: ✅ PASS

- P1: Test by submitting prompt, verify audio playback with character voice
- P2: Test by comparing transformed vs original text for accuracy
- P3: Test voice daemon independently by speaking and checking transcript
- No dependencies between test scenarios

### Principle VI: Documentation Completeness

**Status**: ✅ PASS

- Complete spec.md with user stories, requirements, success criteria
- This plan.md documents technical approach and structure
- Will generate: research.md, data-model.md, quickstart.md, contracts/
- Cross-artifact consistency via /speckit.analyze

**Gate Result**: ✅ ALL PASS - Proceed to Phase 0

### Post-Phase-1 Re-evaluation

**Date**: 2025-11-02
**Status**: ✅ ALL PASS - Design artifacts confirm initial assessment

**Review Summary**:
- **research.md**: No new complexity introduced, all decisions favor simplicity (reuse existing modules, skip transformation for edge cases, accept concurrent audio limitations per YAGNI)
- **data-model.md**: Minimal new entities (Hook Input, Transcript Message), all others reuse existing infrastructure
- **contracts/stop-hook-contract.md**: Simple CLI contract, no abstraction layers, straightforward error handling
- **quickstart.md**: Clear testing path confirms independent testability
- **Agent context updated**: CLAUDE.md reflects new technology stack accurately

**Constitution Compliance Confirmed**:
- Simplicity: Stop hook script <150 lines, single responsibility, no speculative features
- Testability: Quickstart provides independent test scenarios for each user story
- Documentation: All artifacts complete and cross-referenced
- Incremental: P1/P2/P3 priorities maintained through design

**Gate Result**: ✅ PASS - Proceed to Phase 2 (tasks generation)

## Project Structure

### Documentation (this feature)

```text
specs/001-claude-voice-hooks/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── audio/                    # Existing: Audio capture/playback infrastructure
│   ├── capture.py           # Voice input capture with VAD
│   ├── playback.py          # Audio streaming playback
│   └── device_manager.py    # Audio device selection
├── character/               # Existing: Character profile and transformation
│   ├── profile.py           # Character profile data model
│   ├── transformer.py       # Text transformation engine
│   └── profiles/
│       └── toadwart.json    # Character configuration
├── config/                  # Existing: Configuration management
│   ├── voice_config.py      # Voice API configuration
│   └── persistence.py       # Config file I/O
├── hooks/                   # New: Claude Code hook integrations
│   ├── voice_output_hook.py # NEW: Stop hook for voice output (P1)
│   ├── input_hook.py        # Existing: Input submission (future use)
│   └── output_hook.py       # Existing: Response interception (legacy)
├── voice/                   # Existing: Voice processing engines
│   ├── text_to_speech.py    # ElevenLabs TTS integration
│   ├── speech_to_text.py    # OpenAI Whisper transcription
│   ├── output_manager.py    # TTS orchestration
│   └── interaction_manager.py
├── cli.py                   # Existing: CLI interface (not used by hooks)
└── __main__.py

.claude/
└── settings.local.json      # MODIFIED: Hook configuration

tests/
├── hooks/                   # NEW: Hook-specific tests
│   └── test_voice_output_hook.py
├── character/               # Existing: Character tests
└── voice/                   # Existing: Voice tests
```

**Structure Decision**: Single-project structure (Option 1). Feature integrates into existing src/ directories by adding src/hooks/voice_output_hook.py and updating .claude/settings.local.json. Reuses existing voice/character/audio modules without modification. No new top-level directories needed.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: N/A - No constitution violations. All checks passed (see Constitution Check section above).
