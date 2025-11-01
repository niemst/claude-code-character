# Tasks: Voice-Enabled Character Interaction for Claude Code

**Input**: Design documents from `/specs/001-voice-character-interaction/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are NOT included in this implementation (not explicitly requested in feature specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure at repository root
- `src/` - Main source code
- `~/.claude-code/` - User configuration directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure (src/audio, src/voice, src/character, src/config, src/hooks, src/character/profiles)
- [x] T002 Initialize Python project with uv (create pyproject.toml with Python 3.11+ requirement)
- [x] T003 [P] Add core dependencies to pyproject.toml (SpeechRecognition, pyttsx3, pynput, PyAudio or sounddevice)
- [x] T004 [P] Add optional dependencies to pyproject.toml (elevenlabs, openai, edge-tts)
- [x] T005 [P] Configure black formatter in pyproject.toml
- [x] T006 [P] Configure ruff linter in pyproject.toml
- [x] T007 [P] Configure mypy type checker in pyproject.toml
- [x] T008 Create __init__.py files for all packages (src/, src/audio/, src/voice/, src/character/, src/config/, src/hooks/)
- [x] T009 Create .gitignore for Python project (venv/, __pycache__/, *.pyc, .mypy_cache/, .ruff_cache/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Define VoiceConfiguration dataclass in src/config/voice_config.py with type hints
- [x] T011 Implement configuration loader in src/config/persistence.py (load from ~/.claude-code/voice-config.json)
- [x] T012 Implement configuration saver in src/config/persistence.py (save to ~/.claude-code/voice-config.json with chmod 600)
- [x] T013 Create default configuration factory in src/config/voice_config.py (returns VoiceConfiguration with sensible defaults)
- [x] T014 [P] Define CharacterProfile dataclass in src/character/profile.py with validation
- [x] T015 [P] Implement character profile loader in src/character/profile.py (load from src/character/profiles/*.json)
- [x] T016 Create Toudie character profile JSON in src/character/profiles/toudie.json (with voiceId, systemPrompt, phrases per data-model.md)
- [x] T017 [P] Define VoiceSession dataclass in src/voice/voice_session.py for runtime state
- [x] T018 [P] Implement audio device enumeration in src/audio/device_manager.py (list available input/output devices)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Voice Command Input (Priority: P1) 🎯 MVP

**Goal**: Enable hands-free command input through voice with push-to-talk activation, converting speech to text for Claude Code execution

**Independent Test**: Press Ctrl+Space, speak "read file main.py", release Ctrl+Space. Verify that Claude Code receives the text command "read file main.py" and executes it correctly.

### Implementation for User Story 1

- [x] T019 [P] [US1] Implement push-to-talk hotkey listener in src/audio/capture.py using pynput (monitor Ctrl+Space by default)
- [x] T020 [P] [US1] Implement audio capture start/stop in src/audio/capture.py using PyAudio or sounddevice
- [x] T021 [US1] Implement audio recording to in-memory buffer in src/audio/capture.py (capture while push-to-talk active)
- [x] T022 [P] [US1] Implement Web Speech API STT integration in src/voice/speech_to_text.py using SpeechRecognition library
- [x] T023 [P] [US1] Implement Whisper API fallback STT in src/voice/speech_to_text.py (use if Web Speech fails or configured)
- [x] T024 [US1] Implement STT provider selection logic in src/voice/speech_to_text.py (check config, fallback chain)
- [x] T025 [US1] Create voice session manager in src/voice/voice_session.py (track isListening state, lastCommand statistics)
- [x] T026 [US1] Implement push-to-talk press handler in src/audio/capture.py (set isListening=True, start recording)
- [x] T027 [US1] Implement push-to-talk release handler in src/audio/capture.py (set isListening=False, trigger STT)
- [x] T028 [US1] Implement input hook in src/hooks/input_hook.py (send transcribed text to Claude Code command processor)
- [x] T029 [US1] Add visual feedback for push-to-talk active state in src/audio/capture.py (print to console or status indicator)
- [x] T030 [US1] Add error handling for STT failures in src/voice/speech_to_text.py (timeout, network errors, unclear audio)
- [x] T031 [US1] Add performance monitoring in src/voice/voice_session.py (track transcription duration for SC-002 validation)

**Checkpoint**: At this point, User Story 1 should be fully functional - user can issue voice commands that Claude Code executes

---

## Phase 4: User Story 2 - Voice Response Output (Priority: P2)

**Goal**: Convert Claude Code's text responses to speech output, completing the voice interaction loop for fully hands-free operation

**Independent Test**: Issue any command (voice or text). Verify that Claude Code's response is spoken aloud through speakers/headphones.

### Implementation for User Story 2

- [ ] T032 [P] [US2] Implement system TTS integration in src/voice/text_to_speech.py using pyttsx3 (cross-platform fallback)
- [ ] T033 [P] [US2] Implement ElevenLabs TTS integration in src/voice/text_to_speech.py using elevenlabs SDK
- [ ] T034 [US2] Implement TTS provider selection logic in src/voice/text_to_speech.py (check elevenlabs API key, fallback to system)
- [ ] T035 [P] [US2] Implement audio playback in src/audio/playback.py using sounddevice or playsound
- [ ] T036 [P] [US2] Implement audio streaming playback in src/audio/playback.py (start playing while receiving TTS stream)
- [ ] T037 [US2] Implement response queue in src/voice/voice_session.py (FIFO queue for pending responses)
- [ ] T038 [US2] Implement playback state management in src/voice/voice_session.py (track isPlaying, currentAudioStream)
- [ ] T039 [US2] Implement output hook in src/hooks/output_hook.py (intercept Claude Code responses, queue for TTS)
- [ ] T040 [US2] Implement TTS request handler in src/voice/text_to_speech.py (convert text to audio, return stream)
- [ ] T041 [US2] Implement playback controller in src/audio/playback.py (play queued responses sequentially)
- [ ] T042 [US2] Implement interrupt handling in src/audio/playback.py (stop current playback on new push-to-talk press)
- [ ] T043 [US2] Add mutual exclusion enforcement in src/voice/voice_session.py (ensure isListening and isPlaying not both True)
- [ ] T044 [US2] Add performance monitoring in src/voice/voice_session.py (track TTS start latency for SC-003 validation)
- [ ] T045 [US2] Add interrupt response monitoring in src/voice/voice_session.py (track interrupt latency for SC-006 validation)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full voice interaction loop functional

---

## Phase 5: User Story 3 - Character Roleplay for Voice Responses (Priority: P3)

**Goal**: Apply character personality (e.g., Toudie from Gummy Bears) to voice responses only, maintaining 100% technical accuracy in work execution

**Independent Test**: Configure Toudie character, issue any command. Verify that voice responses include character-appropriate phrases ("Great gobs of gummiberries!") while technical content (file names, code) remains unchanged.

### Implementation for User Story 3

- [ ] T046 [P] [US3] Implement character text transformer in src/character/transformer.py (apply personality to response text)
- [ ] T047 [P] [US3] Implement system prompt processor in src/character/transformer.py (use character systemPrompt for transformation)
- [ ] T048 [P] [US3] Implement characteristic phrase injector in src/character/transformer.py (add phrases from character profile)
- [ ] T049 [US3] Implement technical content preservation in src/character/transformer.py (identify and protect code, paths, errors)
- [ ] T050 [US3] Implement character selection logic in src/character/transformer.py (load selected character from config)
- [ ] T051 [US3] Integrate character transformer with output hook in src/hooks/output_hook.py (transform before TTS if character active)
- [ ] T052 [US3] Implement character-specific voice selection in src/voice/text_to_speech.py (use CharacterProfile.voiceId for ElevenLabs)
- [ ] T053 [US3] Implement voice settings application in src/voice/text_to_speech.py (apply stability, similarityBoost from character profile)
- [ ] T054 [US3] Add character transformation tracking in src/voice/voice_session.py (mark responses as characterTransformed)
- [ ] T055 [US3] Add validation for preserveTechnicalContent in src/character/profile.py (enforce must be True)
- [ ] T056 [US3] Implement character switch handling in src/character/transformer.py (apply to next response, not mid-response)

**Checkpoint**: All user stories should now be independently functional - complete voice interaction with optional character roleplay

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final deployment preparation

- [ ] T057 [P] Create main entry point in src/__main__.py (initialize configuration, start voice session, register hooks)
- [ ] T058 [P] Implement configuration CLI commands in src/config/cli.py (config get, config set voice.* commands)
- [ ] T059 [P] Implement voice test commands in src/voice/cli.py (test mic, test tts, test elevenlabs)
- [ ] T060 [P] Implement character list command in src/character/cli.py (list available characters)
- [ ] T061 [P] Implement audio device list command in src/audio/cli.py (list available input/output devices)
- [ ] T062 Add environment variable support for API keys in src/config/persistence.py (OPENAI_API_KEY, ELEVENLABS_API_KEY)
- [ ] T063 Add graceful degradation for missing audio devices in src/audio/device_manager.py (clear error messages)
- [ ] T064 Add configuration validation on load in src/config/persistence.py (check required fields, valid values)
- [ ] T065 [P] Add logging infrastructure using Python logging module (configure in src/__main__.py)
- [ ] T066 Create README.md with installation and quick start instructions (refer to quickstart.md)
- [ ] T067 [P] Create example configuration file at examples/voice-config.example.json
- [ ] T068 Run black formatter on all Python files (ensure PEP 8 compliance)
- [ ] T069 Run ruff linter on all Python files (fix any issues)
- [ ] T070 Run mypy type checker on all Python files (ensure type safety)
- [ ] T071 Validate quickstart.md instructions (test installation and basic voice commands)
- [ ] T072 Verify all Success Criteria from spec.md (SC-001 through SC-008)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1 (can test with text commands)
- **User Story 3 (P3)**: Depends on US2 being complete (needs TTS to apply character voice)

### Within Each User Story

**US1 Tasks:**
- T019-T020 can run in parallel (different concerns)
- T022-T023 can run in parallel (different STT providers)
- T021 depends on T020 (needs capture mechanism)
- T024 depends on T022, T023 (needs both providers to select from)
- T025-T031 sequential (build on each other)

**US2 Tasks:**
- T032-T033 can run in parallel (different TTS providers)
- T035-T036 can run in parallel (different playback methods)
- T034 depends on T032, T033 (needs both providers)
- T037-T045 sequential (build on each other)

**US3 Tasks:**
- T046-T048 can run in parallel (different transformer components)
- T049-T056 sequential (integration tasks)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T007)
- Foundational tasks: T014-T015 and T017-T018 can run in parallel
- Once Foundational phase completes:
  - US1 can be developed
  - US2 can be developed in parallel (different modules)
  - US3 must wait for US2
- Polish tasks marked [P] can run in parallel (T057-T061, T067-T070)

---

## Parallel Example: User Story 1

```bash
# Launch parallelizable tasks for US1 together:
Task T019: "Implement push-to-talk hotkey listener in src/audio/capture.py"
Task T020: "Implement audio capture start/stop in src/audio/capture.py"
Task T022: "Implement Web Speech API STT in src/voice/speech_to_text.py"
Task T023: "Implement Whisper API fallback STT in src/voice/speech_to_text.py"
```

## Parallel Example: User Story 2

```bash
# Launch parallelizable tasks for US2 together:
Task T032: "Implement system TTS in src/voice/text_to_speech.py"
Task T033: "Implement ElevenLabs TTS in src/voice/text_to_speech.py"
Task T035: "Implement audio playback in src/audio/playback.py"
Task T036: "Implement audio streaming playback in src/audio/playback.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T018) - CRITICAL
3. Complete Phase 3: User Story 1 (T019-T031)
4. **STOP and VALIDATE**: Test voice command input independently
   - Verify: User can press Ctrl+Space, speak command, and Claude Code executes it
   - Verify: SC-001 (80% command success rate)
   - Verify: SC-002 (<2s transcription latency)
5. Deploy/demo if ready - **This is a working MVP!**

### Incremental Delivery

1. **MVP (US1)**: Voice command input
   - Zero API keys required (Web Speech API)
   - Hands-free command execution
   - Independent test: Speak any command → Claude executes

2. **Enhancement (US2)**: Add voice response output
   - Still works with zero API keys (system TTS)
   - Complete voice interaction loop
   - Independent test: Any command → Hear spoken response

3. **Polish (US3)**: Add character roleplay
   - Optional ElevenLabs for premium quality
   - Personality without sacrificing accuracy
   - Independent test: Toudie responses include character phrases

Each increment is fully functional and can be deployed independently.

### Parallel Team Strategy

With multiple developers:

1. **All team**: Complete Setup + Foundational together (T001-T018)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (T019-T031)
   - Developer B: User Story 2 (T032-T045) - can work in parallel
3. **After US2 complete**:
   - Developer C: User Story 3 (T046-T056)
4. **All team**: Polish phase (T057-T072)

---

## Notes

- **[P] tasks**: Can run in parallel (different files, no dependencies)
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable
- **No tests**: Tests not included (not requested in spec - optional per plan.md)
- **Commit frequently**: After each task or logical group
- **Checkpoints**: Stop at any checkpoint to validate story independently
- **Python conventions**: snake_case for functions/variables, PascalCase for classes, type hints everywhere
- **Zero-config**: Feature works immediately without API keys (basic quality), upgrades seamlessly when keys added

---

## Success Criteria Validation

At end of implementation, verify all Success Criteria from spec.md:

- [ ] **SC-001**: 80% of common commands successful via voice (test with 20+ commands)
- [ ] **SC-002**: Voice command recognition <2 seconds (measure with voice_session.statistics)
- [ ] **SC-003**: Voice playback starts <1 second (measure with voice_session.statistics)
- [ ] **SC-004**: Character roleplay maintains 100% technical accuracy (test code analysis with Toudie active)
- [ ] **SC-005**: Complete 15+ minute coding session using only voice
- [ ] **SC-006**: Voice interruption responds <500ms (measure with voice_session.statistics)
- [ ] **SC-007**: Character personality in 90%+ of responses when enabled (count Toudie phrases)
- [ ] **SC-008**: Voice toggle in <3 seconds (test enable/disable commands)

---

**Total Tasks**: 72 tasks across 6 phases
**MVP Tasks**: 27 tasks (Setup + Foundational + US1)
**Parallel Opportunities**: 23 tasks marked [P]
**Estimated Timeline**: MVP achievable in 1-2 weeks, full feature in 2-3 weeks
