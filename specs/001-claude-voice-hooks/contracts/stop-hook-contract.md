# Stop Hook Contract

**Feature**: 001-claude-voice-hooks
**Component**: Voice Output Stop Hook
**Type**: CLI Command Contract

## Overview

The Stop Hook is a command-line interface contract between Claude Code and the voice output system. Claude Code invokes the hook as an external command, passing JSON input via stdin and interpreting exit codes and stdout.

## Command Line Interface

### Invocation

```bash
uv run python src/hooks/voice_output_hook.py
```

**Working Directory**: Repository root
**Environment**: Inherits from Claude Code process
**Timeout**: 30 seconds (configurable in .claude/settings.local.json)

### Input (stdin)

**Format**: JSON object via standard input
**Encoding**: UTF-8

**Schema**:
```json
{
  "session_id": "string",
  "transcript_path": "string (absolute file path)",
  "permission_mode": "string",
  "hook_event_name": "string (always 'Stop')",
  "stop_hook_active": "boolean"
}
```

**Required Fields**:
- `transcript_path`: Must be absolute path to existing JSONL file

**Optional Fields**:
- All other fields are informational (logged but not used functionally)

**Example Input**:
```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/my-repo/transcript.jsonl",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

### Output (stdout)

**Normal Operation**: No stdout output (silent execution)

**Optional JSON Response** (for advanced control):
```json
{
  "decision": "allow"
}
```

**Block Stop** (not used in this implementation):
```json
{
  "decision": "block",
  "reason": "Still processing audio"
}
```

**Logging Output**: Sent to stderr, not stdout (does not interfere with Claude Code)

### Exit Codes

**Exit 0**: Success
- Audio playback completed or skipped (e.g., message too short)
- Hook executed without errors
- Claude Code continues normal operation

**Exit 1**: Non-blocking error
- Transcript file not found
- Missing configuration
- TTS API failure
- Claude Code continues, error logged

**Exit 2**: Blocking error (not used)
- Would prevent Claude Code from stopping
- Not applicable to voice output feature

**Exit >2**: Unexpected error
- Treated as Exit 1 (non-blocking)
- Should be avoided, indicates bug

### Execution Flow

```text
1. Read JSON from stdin
2. Validate transcript_path exists
3. Parse JSONL transcript file
4. Extract last assistant message
5. If message empty or <5 chars: Exit 0 (skip TTS)
6. Load character profile
7. Transform text (if <3000 chars, else skip transformation)
8. Load voice configuration
9. Stream TTS from ElevenLabs API
10. Queue and play audio chunks
11. Wait for playback completion
12. Exit 0
```

**Timeout Handling**:
- If elapsed time >25s: Log warning, exit 0
- If Claude Code kills process at 30s: No graceful shutdown (SIGTERM)

### Error Handling Contract

**Principle**: Fail gracefully, never crash Claude Code

**File Not Found** (`transcript_path`):
- Log error to stderr: "Transcript file not found: {path}"
- Exit 1
- Claude Code continues without voice output

**Invalid JSON Input**:
- Log error to stderr: "Failed to parse hook input"
- Exit 1
- Claude Code continues

**Missing Configuration**:
- Log error to stderr: "Voice configuration not found"
- Exit 1
- Claude Code continues

**API Failure** (ElevenLabs):
- Log error to stderr: "TTS synthesis failed"
- Exit 1
- Claude Code continues

**Audio Device Busy**:
- Log error to stderr: "Audio device unavailable"
- Exit 1
- Claude Code continues (concurrent hook may be playing)

**Timeout Approaching** (>25s elapsed):
- Log warning to stderr: "Hook timeout approaching, aborting"
- Exit 0
- Prevents Claude Code forced termination

## Configuration Contract

### Hook Registration

**Location**: `.claude/settings.local.json`

**Schema**:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python src/hooks/voice_output_hook.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Fields**:
- `matcher`: `"*"` matches all stop events
- `command`: Full command to execute hook
- `timeout`: Maximum execution time in seconds (30 recommended)

### Environment Variables

**Optional Configuration**:
- `ELEVENLABS_API_KEY`: ElevenLabs API authentication (if not in config file)
- `OPENAI_API_KEY`: OpenAI API for character transformation (if not in config file)

**Not Required** (defaults from config files):
- Voice configuration: Read from `examples/voice-config.example.json` or similar
- Character profile: Read from `src/character/profiles/toadwart.json`

## Dependencies Contract

**External Commands**:
- `uv`: Python package manager/runner (must be in PATH)
- `python`: Python 3.11+ interpreter (via uv)

**Python Modules** (must be installed):
- `src.character.transformer`: CharacterTransformer class
- `src.character.profile`: CharacterProfile class
- `src.voice.text_to_speech`: TextToSpeechEngine class
- `src.audio.playback`: AudioPlaybackManager class
- `src.config.voice_config`: VoiceConfig class

**External APIs**:
- ElevenLabs TTS API: Requires API key and internet connection
- OpenAI Claude API: Requires API key for character transformation

**Audio System**:
- PyAudio: Requires system audio drivers
- Output device: Must have functional audio output

## Performance Contract

**Latency Targets**:
- First audio chunk: <2 seconds from hook start
- Full synthesis: <5 seconds for messages <1000 chars
- Total execution: <30 seconds (hard limit)

**Resource Limits**:
- Memory: <500MB typical usage
- CPU: Bursts during TTS synthesis, idle during playback
- Network: Streaming TTS, ~100KB/s bandwidth

**Concurrency**:
- Multiple hook instances may run simultaneously
- Audio device conflict is acceptable (one succeeds, others log error and exit 1)
- No coordination between concurrent hooks

## Testing Contract

**Unit Tests**:
```bash
pytest tests/hooks/test_voice_output_hook.py
```

**Integration Test**:
```bash
# 1. Create test transcript
echo '{"role":"assistant","content":[{"type":"text","text":"Test message"}]}' > /tmp/test-transcript.jsonl

# 2. Invoke hook with test input
echo '{"transcript_path":"/tmp/test-transcript.jsonl","session_id":"test","hook_event_name":"Stop","permission_mode":"default","stop_hook_active":false}' | uv run python src/hooks/voice_output_hook.py

# 3. Verify exit code 0 and audio playback occurred
```

**Edge Cases to Test**:
- Empty transcript file
- Transcript with no assistant messages
- Very long message (>5000 chars)
- Missing character profile (should use original text)
- Missing API keys (should fail gracefully)
- Audio device unavailable (should exit 1)

## Backwards Compatibility

**Breaking Changes**: Not applicable (new feature)

**Future Compatibility**:
- Hook input schema may add new fields (ignored safely via JSON parsing)
- Transcript format stable (Claude Code contract)
- Exit codes standard (0=success, 1=error, 2=block)

## Security Contract

**Sandboxing**: Hook runs with same permissions as Claude Code process
- Can read any file readable by user
- Cannot escalate privileges
- Network access allowed (TTS API calls)

**Input Validation**:
- Transcript path must be absolute (no relative paths)
- No shell injection (command executed directly, not via shell)
- JSON parsing protects against malformed input

**Data Privacy**:
- Transcript content sent to external APIs:
  - OpenAI Claude API (character transformation)
  - ElevenLabs API (TTS synthesis)
- API keys logged only as "[redacted]"
- Session IDs logged for debugging (no sensitive data)

**Rate Limiting**:
- No built-in rate limiting (depends on Claude Code invocation frequency)
- API rate limits enforced by external services
- Failures logged, Claude Code continues

## Examples

### Successful Execution

**Input**:
```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/my-repo/transcript.jsonl",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

**Transcript** (`/home/user/.claude/projects/my-repo/transcript.jsonl`):
```json
{"role":"user","content":[{"type":"text","text":"What is 2+2?"}]}
{"role":"assistant","content":[{"type":"text","text":"The answer is 4."}]}
```

**Expected Behavior**:
1. Read transcript, extract "The answer is 4."
2. Transform via character: "*grumble* The answer is 4, youngster"
3. Synthesize speech via ElevenLabs
4. Play audio
5. Exit 0

**Stderr Output**:
```
[INFO] Reading transcript: /home/user/.claude/projects/my-repo/transcript.jsonl
[INFO] Transforming text through character...
[INFO] Synthesizing speech...
[INFO] Speech playback completed
```

### Error: Transcript Not Found

**Input**:
```json
{
  "session_id": "abc123",
  "transcript_path": "/nonexistent/path.jsonl",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

**Expected Behavior**:
1. Attempt to read transcript
2. File not found error
3. Log error
4. Exit 1

**Stderr Output**:
```
[ERROR] Transcript file not found: /nonexistent/path.jsonl
```

### Edge Case: Message Too Short

**Transcript**:
```json
{"role":"assistant","content":[{"type":"text","text":"OK"}]}
```

**Expected Behavior**:
1. Extract "OK" (2 chars)
2. Skip TTS (< 5 chars threshold)
3. Exit 0

**Stderr Output**:
```
[INFO] Reading transcript: ...
[INFO] Assistant message too short, skipping TTS
```
