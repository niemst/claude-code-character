# Implementation Tasks: Claude Code Voice Hooks Integration

**Feature**: 001-claude-voice-hooks
**Branch**: `001-claude-voice-hooks`
**Generated**: 2025-11-02
**Status**: Ready for implementation

## Overview

This document contains the complete task breakdown for implementing Claude Code voice hooks integration. Tasks are organized by user story (P1, P2, P3) to enable independent, incremental delivery following the MVP-first approach.

## Task Summary

- **Total Tasks**: 18
- **Phase 1 (Setup)**: 1 task
- **Phase 2 (User Story 1 - MVP)**: 7 tasks
- **Phase 3 (User Story 2)**: 4 tasks
- **Phase 4 (User Story 3)**: 4 tasks
- **Phase 5 (Polish)**: 2 tasks

## Implementation Strategy

**MVP-First Approach**: Implement User Story 1 (P1) first for complete, testable voice output functionality. User Stories 2 and 3 are enhancements that build on top of US1.

**Independent Delivery**: Each user story can be delivered and tested independently:
- **US1** (P1): Complete voice output - can ship alone
- **US2** (P2): Enhanced character quality - optional improvement to US1
- **US3** (P3): Voice input - completely independent optional feature

**Validation**: After each user story, run the corresponding independent test from quickstart.md to verify completion.

---

## Phase 1: Setup

**Goal**: Configure Claude Code to invoke Stop hook

**Tasks**:

- [X] T001 Configure Stop hook in .claude/settings.local.json per contracts/stop-hook-contract.md

**Completion Criteria**:
- .claude/settings.local.json contains hooks.Stop configuration
- Hook command points to `uv run python src/hooks/voice_output_hook.py`
- Timeout set to 30 seconds

---

## Phase 2: User Story 1 (P1) - Voice Output via Stop Hook

**Goal**: Implement Stop hook that reads Claude responses and plays them as character voice

**Why MVP**: This is the core value proposition - users hear Claude's responses in character voice without changing their workflow.

**Independent Test** (from quickstart.md):
1. Start Claude Code with hook configured
2. Submit text prompt: "What is 2+2?"
3. Verify audio plays with character transformation
4. Check exit code 0 and logs show successful execution

**Tasks**:

- [X] T002 [US1] Create src/hooks/voice_output_hook.py with main() entry point and stdin JSON parsing
- [X] T003 [US1] Implement read_transcript() function to parse JSONL transcript file per data-model.md
- [X] T004 [US1] Implement extract_last_assistant_message() to get text from transcript per contract
- [X] T005 [US1] Integrate CharacterTransformer from src/character/transformer.py for text transformation
- [X] T006 [US1] Integrate TextToSpeechEngine from src/voice/text_to_speech.py for TTS streaming
- [X] T007 [US1] Integrate AudioPlaybackManager from src/audio/playback.py for audio playback
- [X] T008 [US1] Implement error handling (transcript not found, API failures, audio device busy) per contract exit codes
- [X] T009 [US1] Implement timeout handling (skip transformation if >25s elapsed) per research.md decision 5

**Completion Criteria**:
- src/hooks/voice_output_hook.py exists and is executable
- Hook reads JSON from stdin successfully
- Transcript parsing extracts last assistant message
- Character transformation applied (or skipped for long messages)
- TTS streams and plays audio
- Error handling returns appropriate exit codes
- All FR-001 through FR-009, FR-013 through FR-015 implemented

**Dependencies**: Phase 1 must be complete

**Parallel Opportunities**: None (single file implementation)

---

## Phase 3: User Story 2 (P2) - Character Transformation Quality

**Goal**: Validate and enhance character transformer to preserve technical accuracy

**Why Enhancement**: Ensures character voice doesn't break technical content while maintaining personality.

**Independent Test** (from quickstart.md):
1. Submit prompt with code: "Write a Python function to calculate factorial"
2. Compare transformed text with original
3. Verify code snippets, file paths, function names unchanged
4. Confirm character tone applied to prose only

**Tasks**:

- [X] T010 [P] [US2] Verify CharacterTransformer preserves code blocks verbatim in src/character/transformer.py
- [X] T011 [P] [US2] Verify CharacterTransformer preserves file paths unchanged in src/character/transformer.py
- [X] T012 [P] [US2] Test character profile speech patterns integration with src/character/profiles/toadwart.json
- [X] T013 [US2] Add transformation skip logic for responses >3000 chars in src/hooks/voice_output_hook.py

**Completion Criteria**:
- CharacterTransformer validated to preserve technical terms per FR-009
- Long message transformation skip implemented per research.md decision 4
- Character profile speech patterns verified working
- All FR-009 requirements met

**Dependencies**: User Story 1 must be complete (needs working hook)

**Parallel Opportunities**: T010, T011, T012 can run in parallel (different validation scenarios)

---

## Phase 4: User Story 3 (P3) - Voice Input Daemon [OPTIONAL]

**Goal**: Implement background daemon for voice command input

**Why Optional**: Text input works fine, this is an accessibility/hands-free enhancement.

**Independent Test** (from quickstart.md):
1. Start voice daemon in background
2. Speak command: "What is the capital of France?"
3. Verify transcribed text appears as Claude Code user prompt
4. Check VAD filters background noise

**Tasks**:

- [ ] T014 [P] [US3] Create voice input daemon script (separate from Stop hook) [SKIPPED - OPTIONAL]
- [ ] T015 [P] [US3] Integrate OpenAI Whisper transcription from src/voice/speech_to_text.py [SKIPPED - OPTIONAL]
- [ ] T016 [P] [US3] Integrate VAD from src/audio/capture.py for noise filtering [SKIPPED - OPTIONAL]
- [ ] T017 [US3] Implement submission mechanism to Claude Code stdin per FR-012 [SKIPPED - OPTIONAL]

**Completion Criteria**:
- Voice daemon listens continuously for speech
- Whisper transcription working per FR-010
- VAD filters background noise per FR-011
- Transcribed text submitted to Claude Code per FR-012

**Dependencies**: None (completely independent from US1 and US2)

**Parallel Opportunities**: T014, T015, T016 can be developed in parallel (different components)

**Note**: This phase is OPTIONAL. US1 and US2 deliver full value without voice input.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Goal**: Finalize documentation and validate all success criteria

**Tasks**:

- [X] T018 [P] Update quickstart.md with actual file paths and verified test scenarios
- [X] T019 Validate all success criteria SC-001 through SC-007 from spec.md

**Completion Criteria**:
- quickstart.md reflects actual implementation
- All 7 success criteria verified:
  - SC-001: Audio within 5 seconds
  - SC-002: 95% synthesis success rate
  - SC-003: 100% technical accuracy preserved
  - SC-004: Timeout compliance for <1000 char responses
  - SC-005: 90% transcription accuracy (if US3 implemented)
  - SC-006: Claude Code continues on TTS failure
  - SC-007: Non-blocking audio playback

**Dependencies**: All user stories complete

**Parallel Opportunities**: T018 and T019 can run in parallel

---

## Dependency Graph

```text
Phase 1 (Setup)
  └─ T001 Configure hook
       ↓
Phase 2 (US1 - MVP)
  ├─ T002 Create hook script
  ├─ T003 Read transcript
  ├─ T004 Extract message
  ├─ T005 Character transform
  ├─ T006 TTS streaming
  ├─ T007 Audio playback
  ├─ T008 Error handling
  └─ T009 Timeout handling
       ↓
Phase 3 (US2 - Quality) [depends on US1]
  ├─ T010 [P] Verify code preservation
  ├─ T011 [P] Verify path preservation
  ├─ T012 [P] Test speech patterns
  └─ T013 Add skip logic
       ↓
Phase 4 (US3 - Input) [OPTIONAL, independent]
  ├─ T014 [P] Create daemon
  ├─ T015 [P] Whisper integration
  ├─ T016 [P] VAD integration
  └─ T017 Submit to Claude
       ↓
Phase 5 (Polish)
  ├─ T018 [P] Update quickstart
  └─ T019 Validate criteria
```

## User Story Completion Order

1. **First**: User Story 1 (P1) - Phases 1 + 2
   - **Delivers**: Complete voice output functionality (MVP)
   - **Test**: quickstart.md Step 6
   - **Ship**: Yes, standalone value

2. **Second**: User Story 2 (P2) - Phase 3
   - **Delivers**: Enhanced character quality with technical preservation
   - **Test**: quickstart.md Step 7
   - **Ship**: Yes, improves US1

3. **Third**: User Story 3 (P3) - Phase 4 [OPTIONAL]
   - **Delivers**: Voice input for hands-free operation
   - **Test**: quickstart.md voice input test
   - **Ship**: Optional enhancement

4. **Final**: Polish - Phase 5
   - **Delivers**: Validated, documented feature
   - **Test**: All success criteria
   - **Ship**: Required for production

## Parallel Execution Examples

### Within User Story 1 (Sequential)
**Cannot parallelize** - single file implementation (src/hooks/voice_output_hook.py)

All tasks T002-T009 must run sequentially as they build on each other in the same file.

### Within User Story 2
**Can parallelize verification tasks**:
```bash
# Parallel verification
T010 [P] - Verify code preservation (test with code snippet)
T011 [P] - Verify path preservation (test with file paths)
T012 [P] - Test speech patterns (test with character phrases)

# Sequential implementation
T013 - Add skip logic (modifies hook file)
```

### Within User Story 3
**Can parallelize component development**:
```bash
# Parallel development
T014 [P] - Create daemon structure
T015 [P] - Whisper integration (separate test)
T016 [P] - VAD integration (separate test)

# Sequential integration
T017 - Submit mechanism (integrates above)
```

### Polish Phase
**Can fully parallelize**:
```bash
T018 [P] - Documentation update (different file)
T019 [P] - Validation testing (runtime only)
```

## Implementation Notes

### Existing Infrastructure to Reuse

**DO NOT REIMPLEMENT** - these already exist and are tested:
- `src/character/transformer.py` - CharacterTransformer class
- `src/character/profile.py` - CharacterProfile loading
- `src/voice/text_to_speech.py` - TextToSpeechEngine with streaming
- `src/audio/playback.py` - AudioPlaybackManager
- `src/config/voice_config.py` - VoiceConfig loading
- `src/voice/speech_to_text.py` - SpeechToTextEngine (for US3)
- `src/audio/capture.py` - Audio capture with VAD (for US3)

### New Files to Create

**ONLY THESE** need to be created:
- `src/hooks/voice_output_hook.py` - Stop hook main script (US1)
- Voice input daemon script - if implementing US3 (location TBD)

### Configuration Updates

**MODIFY** (not create):
- `.claude/settings.local.json` - Add Stop hook configuration

### Research Decisions to Follow

From research.md:
1. **Stop Hook Integration** (decision 1): Standalone Python script via `uv run`
2. **JSONL Transcript** (decision 2): Line-by-line parsing, reverse iteration
3. **Streaming TTS** (decision 3): Reuse existing `stream_speech()` + `queue_audio()`
4. **Character Transformation** (decision 4): Skip for >3000 chars, reuse existing transformer
5. **Timeout Handling** (decision 5): Hard limit 25s, skip transformation if needed
6. **Concurrent Audio** (decision 6): Accept device conflict, log error (YAGNI)

### Contract Requirements

From contracts/stop-hook-contract.md:
- **Input**: JSON via stdin with transcript_path
- **Output**: Silent (no stdout), logging to stderr
- **Exit codes**: 0 (success), 1 (non-blocking error)
- **Timeout**: 30 seconds max execution
- **Logging**: Use logging module with INFO/ERROR levels

### Code Quality Standards

Per constitution.md:
- Python 3.11+ with type hints
- Use logging module (no print statements)
- Exception logging with exc_info=True
- No emojis in code/commits
- SOLID, Clean Code, DRY principles
- Functions <20 lines where possible
- Meaningful names, no magic numbers

## Testing Strategy

**No Unit Tests Required** - spec.md does not request TDD or unit tests.

**Integration Testing** - Use quickstart.md scenarios:
1. **US1 Test**: Submit prompt, verify audio playback
2. **US2 Test**: Code example, verify preservation
3. **US3 Test**: Voice input, verify transcription (if implemented)

**Success Criteria Validation** - Phase 5, T019:
- Run all 7 success criteria checks from spec.md
- Document pass/fail for each criterion
- Fix any failures before marking US complete

## Completion Validation

**Feature Complete** when:
- [ ] All Phase 1 and Phase 2 tasks (US1) complete - **MVP READY**
- [ ] All Phase 3 tasks (US2) complete - **ENHANCED QUALITY**
- [ ] All Phase 4 tasks (US3) complete OR explicitly skipped - **OPTIONAL**
- [ ] All Phase 5 tasks complete - **PRODUCTION READY**
- [ ] All success criteria SC-001 through SC-007 validated
- [ ] Independent tests from quickstart.md pass for implemented user stories
- [ ] No failing tasks in dependency graph

**Ship Decision Points**:
1. After Phase 2: Can ship US1 as MVP
2. After Phase 3: Can ship US1 + US2 with enhanced quality
3. After Phase 4: Can ship full feature with voice input
4. After Phase 5: Must complete before production release

## Next Steps

1. Execute tasks in order: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. Mark each task complete with `[X]` when done
3. Run independent test after each user story completion
4. Use `/speckit.analyze` to verify cross-artifact consistency before final ship
5. Create pull request after Phase 5 complete

---

**Total Tasks**: 18
**Parallel Opportunities**: 6 tasks can run in parallel (T010-T012, T014-T016, T018-T019)
**Sequential Requirements**: Phases must complete in order (1→2→3→4→5)
**MVP Scope**: Phases 1 + 2 (Tasks T001-T009) - 9 tasks for complete MVP
