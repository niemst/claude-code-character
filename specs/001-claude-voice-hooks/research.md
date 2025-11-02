# Research: Claude Code Voice Hooks Integration

**Feature**: 001-claude-voice-hooks
**Phase**: Phase 0 - Research & Technical Discovery
**Date**: 2025-11-02

## Research Areas

### 1. Claude Code Stop Hook Integration

**Question**: How to properly integrate Python scripts as Claude Code Stop hooks?

**Research Findings**:

- **Hook Invocation**: Claude Code invokes hooks as shell commands with JSON input via stdin
- **Input Schema**: Stop hook receives `{session_id, transcript_path, permission_mode, hook_event_name, stop_hook_active}`
- **Transcript Path**: Absolute path to JSONL file containing conversation history
- **Timeout**: Configurable via `timeout` parameter (default should respect user settings, typical 30-60s)
- **Exit Codes**:
  - Exit 0: Success
  - Exit 2: Blocking error (hook can prevent stop with `"decision": "block"` in JSON output)
  - Other codes: Non-blocking errors
- **Non-Blocking**: Hook execution should not block Claude Code from accepting next user prompt
- **Error Handling**: Failures should log but not crash Claude Code session

**Decision**: Implement Stop hook as standalone Python script invoked via `uv run python src/hooks/voice_output_hook.py`

**Rationale**: Matches Claude Code's command-based hook system, allows easy testing, leverages existing Python environment via uv

**Alternatives Considered**:
- Shell script wrapper: Rejected - adds unnecessary layer, Python can handle JSON I/O directly
- Inline subprocess: Rejected - hook needs to be external command per Claude Code design

### 2. JSONL Transcript Format

**Question**: What is the structure of Claude Code's JSONL transcript files?

**Research Findings**:

- **Format**: One JSON object per line (newline-delimited JSON)
- **Message Structure**: Each line is a message object with `role` field
- **Role Types**: `user` (user prompts) and `assistant` (Claude responses)
- **Content Field**: Array of content blocks, each with `type` and data
- **Text Blocks**: `{type: "text", text: "content"}`
- **Tool Use Blocks**: `{type: "tool_use", ...}` (not needed for voice output)
- **Reading Strategy**: Read file, parse each line as JSON, filter by role=assistant, extract text blocks
- **Last Message**: Iterate in reverse to find most recent assistant message

**Decision**: Read transcript line-by-line, parse JSON, extract text from last assistant message's content blocks

**Rationale**: Simple, robust parsing that handles large transcripts without loading entire file into memory

**Alternatives Considered**:
- Load entire file: Rejected - memory inefficient for long conversations
- Regex parsing: Rejected - fragile, JSON parsing is safer

### 3. Streaming TTS for Large Responses

**Question**: How to handle TTS for responses exceeding 1000 characters without blocking?

**Research Findings**:

- **ElevenLabs Streaming**: API supports streaming via `/v1/text-to-speech/{voice_id}/stream` endpoint
- **Chunking Strategy**: API returns audio chunks as they're generated
- **Queue Pattern**: Producer-consumer pattern with audio queue
- **Playback While Generating**: Start playback as soon as first chunk arrives
- **Latency Reduction**: User hears audio within 1-2 seconds instead of waiting for full generation
- **Existing Implementation**: `src/voice/text_to_speech.py` already implements `stream_speech()` method
- **Existing Playback**: `src/audio/playback.py` has `queue_audio()` for chunk-based playback

**Decision**: Use existing `TextToSpeechEngine.stream_speech()` with `AudioPlaybackManager.queue_audio()`

**Rationale**: Infrastructure already exists and tested, no need to rebuild

**Alternatives Considered**:
- Batch TTS: Rejected - high latency for long responses
- Split into sentences: Rejected - adds complexity, streaming API handles this

### 4. Character Transformation Accuracy

**Question**: How to preserve technical accuracy (code, paths, commands) while applying character personality?

**Research Findings**:

- **Existing Infrastructure**: `src/character/transformer.py` already implements `transform_output()`
- **Preservation Patterns**:
  - Detect code blocks via markdown fences (```)
  - Detect file paths via regex patterns (`/`, `\`, `.ext`)
  - Detect commands via shell syntax patterns
- **Transformation Approach**: Apply personality to prose, preserve technical literals
- **Current Implementation**: CharacterTransformer uses Claude API to transform text with preservation instructions
- **Prompt Engineering**: Transformer includes rules like "preserve code blocks verbatim", "keep file paths unchanged"

**Decision**: Reuse existing `CharacterTransformer.transform_output()` without modification

**Rationale**: Current implementation already handles preservation requirements, tested in existing voice interaction system

**Alternatives Considered**:
- Manual regex replacement: Rejected - existing AI-based approach more robust
- Post-processing validation: Rejected - adds complexity, existing method sufficient

### 5. Hook Timeout Handling

**Question**: How to ensure hook completes within timeout (30s default) and gracefully handles failures?

**Research Findings**:

- **Claude Code Enforcement**: Timeout is enforced by Claude Code, script will be killed if exceeded
- **Typical Execution Time**:
  - Transcript read: <100ms
  - Character transformation (Claude API): 1-3s
  - TTS streaming start: 1-2s
  - Total: ~2-5s for most responses
- **Timeout Risk**: Long responses (5000+ chars) with transformation might exceed 30s
- **Mitigation Strategies**:
  - Skip transformation for very long responses (>3000 chars)
  - Set TTS timeout independently
  - Use asyncio/threading to run TTS in background (tricky - hook must exit)
- **Error Recovery**: If timeout imminent, log error and exit cleanly

**Decision**:
1. Skip character transformation for responses >3000 characters (use original text)
2. Set hard limit: if elapsed time >25s, stop processing and exit 0
3. Log all timeouts for monitoring

**Rationale**: Balances quality (character voice for normal responses) with reliability (always completes within timeout)

**Alternatives Considered**:
- Background daemon: Rejected - adds complexity, hook model is stateless
- Increase timeout: Rejected - user setting, can't control
- Always skip transformation: Rejected - defeats purpose of character feature

### 6. Concurrent Audio Playback

**Question**: How to handle multiple rapid responses (e.g., user sends multiple prompts quickly)?

**Research Findings**:

- **Hook Invocation Model**: Each Stop event triggers separate hook process
- **Process Isolation**: Multiple hook instances can run concurrently
- **Audio Device Conflict**: Only one process can play audio at a time (hardware limitation)
- **Queueing Options**:
  - OS-level audio mixing: Not reliable
  - Shared queue file/socket: Complex IPC
  - Audio device locking: Simple but blocks concurrent hooks
- **Current Behavior**: AudioPlaybackManager uses PyAudio, which blocks device during playback
- **Failure Mode**: Second hook fails to open audio device if first is playing

**Decision**: Accept concurrent audio limitation - second hook logs error and exits if device busy

**Rationale**: Edge case (rapid responses), adding IPC for queueing adds significant complexity, violates YAGNI

**Alternatives Considered**:
- Shared audio daemon: Rejected - requires persistent process, complex state management
- Redis/queue: Rejected - overkill for rare edge case
- Mix audio streams: Rejected - OS doesn't support reliably across platforms

## Technology Stack Summary

**Confirmed Technologies**:
- Python 3.11+ (existing project standard)
- Claude Code Stop hooks (native integration mechanism)
- ElevenLabs streaming TTS API (existing integration in src/voice/text_to_speech.py)
- OpenAI Claude API (existing integration in src/character/transformer.py)
- PyAudio (existing audio playback in src/audio/playback.py)
- Standard library: json, logging, pathlib

**New Dependencies**: None - all required libraries already in project

**Configuration Files**:
- .claude/settings.local.json (hook registration)
- src/character/profiles/*.json (character definitions)
- Voice config (API keys, voice ID) via environment or existing config system

## Assumptions

1. User has configured ElevenLabs and OpenAI API keys (existing requirement)
2. Audio output device is available and functional
3. Claude Code is running in terminal environment (not headless)
4. Hook timeout is at least 30 seconds (Claude Code default)
5. User wants character transformation for all responses (configurable via profile)

## Open Questions

None - all research areas resolved with concrete decisions.
