# Data Model: Claude Code Voice Hooks Integration

**Feature**: 001-claude-voice-hooks
**Phase**: Phase 1 - Design Artifacts
**Date**: 2025-11-02

## Overview

This feature integrates with existing data models from the voice interaction system (character profiles, voice configuration, audio streams) and introduces Stop hook integration data. Most entities already exist; this document focuses on hook-specific data structures and their relationships.

## Entities

### Hook Input (External - Claude Code)

**Source**: Claude Code Stop hook invocation
**Format**: JSON via stdin
**Lifecycle**: Read-only, one-time input per hook execution

**Fields**:
- `session_id` (string): Unique identifier for Claude Code session
- `transcript_path` (string): Absolute file path to JSONL transcript
- `permission_mode` (string): Claude Code permission mode (e.g., "default")
- `hook_event_name` (string): Always "Stop" for this integration
- `stop_hook_active` (boolean): Indicates if Stop hook previously triggered continuation

**Relationships**: None (external input)

**Validation**:
- `transcript_path` must exist and be readable
- `session_id` is logged for debugging but not used functionally

**Example**:
```json
{
  "session_id": "abc123def456",
  "transcript_path": "/home/user/.claude/projects/my-project/transcript.jsonl",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

---

### Transcript Message (External - Claude Code)

**Source**: JSONL transcript file (`transcript_path` from Hook Input)
**Format**: One JSON object per line (newline-delimited JSON)
**Lifecycle**: Read-only, historical conversation data

**Fields**:
- `role` (string): Either "user" or "assistant"
- `content` (array): List of content blocks

**Content Block Types**:
- Text block: `{type: "text", text: string}`
- Tool use block: `{type: "tool_use", ...}` (ignored by voice output)

**Relationships**:
- Multiple messages in transcript
- Hook extracts last message where `role == "assistant"`

**Validation**:
- Must have at least one text block in content array
- Text must be non-empty after stripping whitespace

**Example**:
```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I've updated the file successfully."},
    {"type": "tool_use", "id": "...", "name": "Edit", "input": {...}}
  ]
}
```

---

### Character Profile (Existing)

**Source**: `src/character/profiles/{character_name}.json`
**Implementation**: `src/character/profile.py` - `CharacterProfile` class
**Lifecycle**: Loaded once per hook execution, cached in transformer

**Fields**:
- `name` (string): Character identifier (e.g., "toadwart")
- `description` (string): Character backstory and personality
- `traits` (array of strings): Personality traits
- `speech_patterns` (array of strings): Characteristic phrases
- `transformation_rules` (array of strings): Instructions for text transformation

**Relationships**:
- Used by CharacterTransformer to modify assistant text
- Referenced in Voice Configuration for active character selection

**Validation**:
- File must exist at expected path
- All fields required
- Falls back to no transformation if profile missing

**Example**:
```json
{
  "name": "toadwart",
  "description": "A grumpy but lovable toad wizard",
  "traits": ["grumpy", "sarcastic", "wise"],
  "speech_patterns": ["*grumble*", "youngster", "back in my day"],
  "transformation_rules": [
    "Preserve all code blocks verbatim",
    "Keep file paths unchanged",
    "Add grumpy tone to explanations"
  ]
}
```

---

### Voice Configuration (Existing)

**Source**: Configuration file or environment variables
**Implementation**: `src/config/voice_config.py` - `VoiceConfig` class
**Lifecycle**: Loaded once per hook execution

**Fields**:
- `elevenlabs_api_key` (string, secret): ElevenLabs API authentication
- `voice_id` (string): ElevenLabs voice identifier for TTS
- `model_id` (string): ElevenLabs model (e.g., "eleven_turbo_v2")
- `sample_rate` (integer): Audio sample rate in Hz (default 22050)
- `playback_chunk_size` (integer): Audio chunk size for streaming (default 4096)

**Relationships**:
- Used by TextToSpeechEngine for API calls
- Used by AudioPlaybackManager for playback configuration

**Validation**:
- `elevenlabs_api_key` must be non-empty
- `voice_id` must be valid ElevenLabs voice ID
- `sample_rate` must be supported (22050, 44100, or 48000)

**Example**:
```python
VoiceConfig(
    elevenlabs_api_key="sk_...",  # pragma: allowlist secret
    voice_id="21m00Tcm4TlvDq8ikWAM",
    model_id="eleven_turbo_v2",
    sample_rate=22050,
    playback_chunk_size=4096
)
```

---

### Transformed Text (Transient)

**Source**: CharacterTransformer output
**Format**: Plain string
**Lifecycle**: In-memory only, not persisted

**Fields**:
- Original text (input): Raw assistant message from transcript
- Transformed text (output): Character-modified version for TTS

**Relationships**:
- Input to TextToSpeechEngine
- Derived from Transcript Message + Character Profile

**Validation**:
- Length <3000 chars (transformation skipped if longer per research.md)
- Technical terms preserved (validated by transformer prompt)
- Non-empty after transformation

**Example**:
```python
# Original
"I've updated the configuration file at src/config/voice_config.py"

# Transformed (toadwart character)
"*grumble* Fine, fine, I've meddled with your configuration file at src/config/voice_config.py, youngster"
```

---

### Audio Stream (Transient)

**Source**: ElevenLabs TTS API streaming response
**Format**: Binary audio chunks (PCM or MP3)
**Lifecycle**: Streamed and played, not persisted

**Fields**:
- Chunk data (bytes): Raw audio data
- Chunk sequence: Ordered by generation time
- Format: Determined by API (typically PCM 16-bit)

**Relationships**:
- Generated from Transformed Text
- Consumed by AudioPlaybackManager

**Validation**:
- Non-empty chunks
- Playback continues until final chunk marker

---

## Data Flow

```text
1. Hook Input (JSON stdin)
   ↓
2. Read Transcript Path
   ↓
3. Parse Transcript Messages (JSONL)
   ↓
4. Extract Last Assistant Message
   ↓
5. Load Character Profile
   ↓
6. Transform Text (Character Transformer)
   ↓
7. Load Voice Configuration
   ↓
8. Generate Audio Stream (ElevenLabs TTS)
   ↓
9. Queue Audio Chunks (Playback Manager)
   ↓
10. Play Audio (PyAudio)
```

## State Management

**Stateless Hook Design**: Each hook invocation is independent
- No persistent state between executions
- No shared memory with other hook instances
- Configuration loaded fresh each time

**Concurrency**:
- Multiple hook instances may run simultaneously (different sessions)
- Audio device conflict handled by error logging (see research.md)
- No synchronization mechanisms needed (stateless design)

## Error Handling

**Missing Data**:
- Transcript file not found: Log error, exit 1
- No assistant message: Log warning, exit 0 (normal termination)
- Character profile missing: Log warning, use original text, continue
- Voice config missing: Log error, exit 1

**Invalid Data**:
- Malformed JSON transcript: Log error, exit 1
- Empty assistant text: Log info, exit 0
- Invalid API keys: Log error during TTS, exit 1

**Timeout**:
- Transformation >25s elapsed: Skip transformation, use original text
- Total execution >30s: Terminated by Claude Code (no graceful handling possible)

## Security Considerations

**Sensitive Data**:
- API keys: Read from environment/config, never logged
- Transcript content: May contain user code/data, handle securely
- Session IDs: Log for debugging only, no sensitive data exposure

**File Access**:
- Transcript path: Validated as absolute path, no directory traversal
- Character profiles: Read-only access to known directory
- No file writes (read-only hook)

## Future Extensions (Not in Scope)

- Voice input daemon data model (P3 user story)
- UserPromptSubmit hook integration (input transformation)
- Persistent audio history/cache
- Multi-character profile switching
