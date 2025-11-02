# Quickstart Guide: Claude Code Voice Hooks Integration

**Feature**: 001-claude-voice-hooks
**Time to Complete**: 10 minutes
**Prerequisites**: Claude Code installed, Python 3.11+, audio output device

## Overview

This guide walks you through setting up and testing voice output integration with Claude Code. You'll configure the Stop hook, verify your setup, and test character-transformed voice responses.

## Prerequisites Check

Before starting, verify you have:

**Required**:
- [ ] Claude Code CLI installed and working
- [ ] Python 3.11 or higher (`python --version`)
- [ ] uv package manager (`uv --version`)
- [ ] Audio output device (speakers/headphones)
- [ ] Internet connection (for TTS API)

**API Keys** (required):
- [ ] ElevenLabs API key ([get one here](https://elevenlabs.io))
- [ ] OpenAI API key for character transformation ([get one here](https://platform.openai.com))

**Verify Prerequisites**:
```bash
# Check Python version
python --version  # Should show 3.11 or higher

# Check uv
uv --version

# Check Claude Code
claude --version

# Verify repository
cd /path/to/claude-code-character
ls src/hooks/voice_output_hook.py  # Should exist after implementation
```

## Step 1: Install Dependencies

```bash
# Navigate to repository root
cd /path/to/claude-code-character

# Install Python dependencies
uv sync

# Verify installation
uv run python -c "import elevenlabs; print('ElevenLabs SDK installed')"
uv run python -c "import openai; print('OpenAI SDK installed')"
```

**Expected Output**:
```
ElevenLabs SDK installed
OpenAI SDK installed
```

**Troubleshooting**:
- If `uv sync` fails: Check `pyproject.toml` has correct dependencies
- If imports fail: Run `uv pip install elevenlabs openai`

## Step 2: Configure API Keys

**Option A: Environment Variables** (recommended for testing)

```bash
# Linux/macOS
export ELEVENLABS_API_KEY="your_elevenlabs_api_key_here"  # pragma: allowlist secret
export OPENAI_API_KEY="your_openai_api_key_here"  # pragma: allowlist secret

# Windows PowerShell
$env:ELEVENLABS_API_KEY="your_elevenlabs_api_key_here"  # pragma: allowlist secret
$env:OPENAI_API_KEY="your_openai_api_key_here"  # pragma: allowlist secret
```

**Option B: Configuration File**

Create or update `config/voice-config.json`:
```json
{
  "elevenlabs_api_key": "your_elevenlabs_api_key_here",  // pragma: allowlist secret
  "openai_api_key": "your_openai_api_key_here",  // pragma: allowlist secret
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "model_id": "eleven_turbo_v2",
  "sample_rate": 22050
}
```

**Verify Configuration**:
```bash
# Test voice configuration loading
uv run python -c "from src.config.voice_config import VoiceConfig; c = VoiceConfig.from_config_file(); print('Config loaded successfully')"
```

## Step 3: Configure Character Profile

The default character profile (toadwart) should already exist. Verify:

```bash
# Check character profile exists
cat src/character/profiles/toadwart.json
```

**Expected Output**: JSON with `name`, `description`, `traits`, `speech_patterns`, `transformation_rules`

**Optional: Create Custom Character**

Create `src/character/profiles/mycharacter.json`:
```json
{
  "name": "mycharacter",
  "description": "A helpful and enthusiastic coding assistant",
  "traits": ["helpful", "enthusiastic", "clear"],
  "speech_patterns": ["Awesome!", "Let's do this!", "Great question!"],
  "transformation_rules": [
    "Preserve all code blocks verbatim",
    "Keep file paths unchanged",
    "Add encouraging tone to explanations"
  ]
}
```

Update `voice_output_hook.py` to use your character:
```python
# Change line: character_name = "toadwart"
# To: character_name = "mycharacter"
```

## Step 4: Configure Stop Hook

Edit `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "SlashCommand(/speckit.tasks)",
      "Bash(pwsh:*)",
      "Bash(python -m black:*)",
      "Bash(python -m ruff check:*)"
    ],
    "ask": [],
    "deny": []
  },
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

**Key Configuration**:
- `matcher`: `"*"` triggers hook for all Stop events
- `command`: Full command to invoke hook (must be absolute or in PATH)
- `timeout`: 30 seconds (adjust if needed for long responses)

**Verify Configuration**:
```bash
# Check JSON syntax is valid
cat .claude/settings.local.json | python -m json.tool
```

## Step 5: Test Hook Manually

Before testing with Claude Code, verify the hook works standalone:

**Create Test Transcript**:
```bash
# Create temporary test transcript
cat > /tmp/test-transcript.jsonl << 'EOF'
{"role":"user","content":[{"type":"text","text":"What is 2+2?"}]}
{"role":"assistant","content":[{"type":"text","text":"The answer is 4. It's a simple arithmetic operation."}]}
EOF
```

**Invoke Hook Manually**:
```bash
# Prepare test input
echo '{"session_id":"test","transcript_path":"/tmp/test-transcript.jsonl","permission_mode":"default","hook_event_name":"Stop","stop_hook_active":false}' | uv run python src/hooks/voice_output_hook.py

# Check exit code
echo $?  # Should be 0
```

**Expected Behavior**:
1. Hook reads transcript
2. Extracts "The answer is 4. It's a simple arithmetic operation."
3. Transforms via character (e.g., "*grumble* The answer is 4, youngster...")
4. Synthesizes speech via ElevenLabs
5. Plays audio through speakers
6. Exits with code 0

**Verify**:
- [ ] Hear audio playback (character voice)
- [ ] Exit code is 0
- [ ] No error messages in stderr

**Troubleshooting**:
- **No audio**: Check volume, verify audio device works with other apps
- **Exit code 1**: Check stderr for error messages
- **API errors**: Verify API keys are correct and have sufficient credits
- **Timeout**: Reduce message length or increase timeout in settings

## Step 6: Test with Claude Code

**Start Claude Code Session**:
```bash
# Navigate to repository
cd /path/to/claude-code-character

# Start Claude Code
claude
```

**Submit Test Prompt**:
```
You: What is the capital of France?
```

**Expected Behavior**:
1. Claude responds with text answer
2. Stop hook automatically triggers
3. Audio playback occurs with character transformation
4. You hear the response spoken aloud

**Verify**:
- [ ] Claude's text response appears in terminal
- [ ] Audio plays automatically after response
- [ ] Character transformation applied (e.g., grumpy tone for toadwart)
- [ ] Next prompt accepted normally (no blocking)

## Step 7: Test Edge Cases

### Test: Short Response (Should Skip TTS)

```
You: Say "OK"
```

**Expected**: Claude responds "OK", no audio playback (message too short)

### Test: Long Response (Should Stream TTS)

```
You: Explain the history of Python programming language in detail
```

**Expected**: Long response streams audio progressively, not all at once

### Test: Code Response (Should Preserve Code)

```
You: Write a Python function to calculate factorial
```

**Expected**:
- Audio includes code explanation
- Code snippets preserved in transformation (not garbled)
- File paths/function names unchanged

### Test: Rapid Responses

```
You: What is 1+1?
```

Immediately after audio starts:

```
You: What is 2+2?
```

**Expected**:
- First audio plays
- Second hook may fail (audio device busy) - this is acceptable
- OR second audio queues and plays after first (depends on timing)

## Step 8: Verify Logging

Check hook execution logs:

```bash
# Claude Code logs are in stderr during session
# Look for lines like:
# [INFO] Reading transcript: ...
# [INFO] Transforming text through character...
# [INFO] Synthesizing speech...
# [INFO] Speech playback completed
```

**Verify Log Output**:
- [ ] No ERROR messages (except acceptable "audio device busy")
- [ ] INFO messages show successful execution
- [ ] No WARNING about timeout approaching

## Step 9: Performance Validation

Test against success criteria from spec:

**SC-001**: User hears audio response within 5 seconds
```
You: What is 2+2?
```
- [ ] Audio starts within 5 seconds of Claude finishing text response

**SC-002**: 95% of responses successfully synthesized
- [ ] Test 10 different prompts
- [ ] At least 9 should play audio without errors

**SC-003**: Technical accuracy preserved
```
You: Show me the path to the config file
```
- [ ] File path in audio matches text exactly (no transformation)

**SC-004**: Hook completes within timeout for <1000 char responses
```
You: Explain variables in Python
```
- [ ] Check logs show completion time <30s
- [ ] No timeout warnings

**SC-006**: System continues on TTS failures
```bash
# Temporarily break API key to simulate failure
export ELEVENLABS_API_KEY="invalid_key"  # pragma: allowlist secret

# Start Claude Code and submit prompt
You: What is 2+2?
```
- [ ] Text response appears normally
- [ ] Hook logs error, exits 1
- [ ] Claude Code accepts next prompt without issue

**SC-007**: Audio doesn't block prompt processing
```
You: Count to 100
```

While audio is playing:
```
You: What is 2+2?
```
- [ ] Can submit new prompt while previous audio plays

## Success Criteria

Your setup is working if:

- [x] All prerequisites installed
- [x] API keys configured and validated
- [x] Character profile loaded
- [x] Stop hook registered in Claude Code settings
- [x] Manual test plays audio successfully
- [x] Claude Code integration triggers audio automatically
- [x] Edge cases handled gracefully
- [x] Performance meets success criteria

## Troubleshooting Guide

### Problem: No audio playback

**Symptoms**: Hook executes (exit 0) but no sound

**Solutions**:
1. Check system volume/unmuted
2. Verify audio device: `python -c "import pyaudio; p=pyaudio.PyAudio(); print(p.get_default_output_device_info())"`
3. Test TTS directly: `uv run python -c "from src.voice.text_to_speech import TextToSpeechEngine; ..."`
4. Check ElevenLabs API quota/credits

### Problem: Exit code 1 (errors)

**Symptoms**: Hook fails, stderr shows errors

**Solutions by Error Message**:
- "Transcript file not found": Check transcript_path in test input, verify file exists
- "Voice configuration not found": Verify API keys configured (Step 2)
- "TTS synthesis failed": Check API key validity, internet connection, ElevenLabs status
- "Audio device unavailable": Close other audio apps, check device not in use

### Problem: Timeout (hook killed at 30s)

**Symptoms**: Long responses cut off, stderr shows timeout

**Solutions**:
1. Increase timeout in `.claude/settings.local.json` to 60
2. Reduce message length (transformation skipped for >3000 chars)
3. Check internet speed (slow TTS API calls)

### Problem: Character transformation not working

**Symptoms**: Audio plays but sounds like normal response, no personality

**Solutions**:
1. Verify character profile exists: `cat src/character/profiles/toadwart.json`
2. Check OPENAI_API_KEY configured
3. Test transformation directly: `uv run python -c "from src.character.transformer import CharacterTransformer; ..."`
4. Check stderr for transformation errors (may fall back to original text)

### Problem: Concurrent audio conflicts

**Symptoms**: Second response fails with "audio device busy"

**Solutions**:
- This is expected behavior (research.md decision)
- Wait for first audio to complete before next prompt
- OR ignore error (Claude Code continues normally, only audio skipped)

## Next Steps

After successful quickstart:

1. **Customize Character**: Edit `src/character/profiles/toadwart.json` to adjust personality
2. **Voice Selection**: Change `voice_id` in voice config to different ElevenLabs voice
3. **Implement P3** (optional): Voice input daemon for hands-free interaction
4. **Run Tests**: `pytest tests/hooks/` to verify implementation
5. **Performance Tuning**: Adjust `sample_rate`, `chunk_size` for quality/latency trade-offs

## Feedback & Issues

If you encounter problems not covered in this guide:

1. Check logs in stderr during Claude Code session
2. Review hook contract: `specs/001-claude-voice-hooks/contracts/stop-hook-contract.md`
3. Verify data model: `specs/001-claude-voice-hooks/data-model.md`
4. Report issues with:
   - Error messages from logs
   - Steps to reproduce
   - Expected vs actual behavior
