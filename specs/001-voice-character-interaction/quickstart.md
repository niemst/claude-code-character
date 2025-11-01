# Quickstart: Voice-Enabled Character Interaction

**Feature**: Voice commands and voice responses for Claude Code with optional character roleplay
**Time to first voice command**: <5 minutes (no API keys required!)
**Last Updated**: 2025-11-01

## TL;DR - Zero Configuration Start

```bash
# 1. Enable voice features (works immediately with system services)
claude-code config set voice.enabled true

# 2. Start using voice commands
# Press Ctrl+Space, speak: "read file package.json"
# Claude Code responds with voice!
```

**That's it!** No API keys, no setup, no cost. Voice features work immediately using:
- Web Speech API for speech recognition (free)
- System TTS for voice output (free)

Want better quality? Add ElevenLabs API key (optional, see [Premium Setup](#premium-setup-optional)).

---

## Quick Start (Basic - Free)

### Prerequisites

- Python 3.11+ installed
- `uv` installed ([install guide](https://github.com/astral-sh/uv))
- Working microphone and speakers
- Supported OS: Windows 10+, macOS 10.14+, or Linux with PulseAudio

### Step 1: Install

```bash
# Clone repository
git clone https://github.com/your-org/claude-code-voice.git
cd claude-code-voice

# Install with uv (automatically creates venv and installs deps)
uv sync

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Enable Voice Features

```bash
# Enable voice input and output
python -m claude_code_voice config set voice.input true
python -m claude_code_voice config set voice.output true

# Configure push-to-talk key (default: Ctrl+Space)
python -m claude_code_voice config set voice.pushToTalkKey "Ctrl+Space"
```

### Step 3: Test Voice Command

1. Start Claude Code with voice: `python -m claude_code_voice`
2. Press and hold **Ctrl+Space**
3. Speak: **"List files in current directory"**
4. Release **Ctrl+Space**
5. Listen to Claude Code's voice response!

**✅ Success**: You should hear Claude Code respond and see the file list.

---

## Premium Setup (Optional)

For superior voice quality and custom character voices, add ElevenLabs API key:

### Step 1: Get ElevenLabs API Key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Choose a plan:
   - **Free**: 10,000 chars/month (limited)
   - **Creator**: $5/month for 30,000 chars
   - **Independent Publisher**: $22/month for 100,000 chars (recommended)
3. Copy your API key from Settings → API Keys

### Step 2: Configure ElevenLabs

```bash
# Add ElevenLabs API key (voice output automatically upgrades)
python -m claude_code_voice config set voice.apiKeys.elevenlabs "your-api-key-here"

# Optional: explicitly set TTS provider
python -m claude_code_voice config set voice.ttsConfig.provider "elevenlabs"

# Optional: choose ElevenLabs model
python -m claude_code_voice config set voice.ttsConfig.elevenlabsModel "eleven_multilingual_v2"
```

### Step 3: Enable Character Roleplay

```bash
# Activate Toudie character (from Gummy Bears)
python -m claude_code_voice config set voice.selectedCharacter "toudie"
```

Now your responses will be spoken in Toudie's voice with personality!

**Example response**: *"Great gobs of gummiberries! File package.json has been read successfully, friend! It contains 47 lines..."*

---

## Feature Overview

### What Works Out-of-the-Box (Free)

✅ **Voice Input (STT)**:
- Press Ctrl+Space to activate microphone
- Speak your command in Polish or English
- Release Ctrl+Space to process

✅ **Voice Output (TTS)**:
- Claude Code responses spoken aloud
- System TTS (Windows/macOS/Linux)
- Character text transformation (personality in words)

✅ **Character Roleplay**:
- Text-based personality (e.g., Toudie's phrases)
- Works with both system and premium TTS

### What Improves with ElevenLabs (Paid)

✨ **Premium Voice Quality**:
- Natural, expressive speech
- Emotional range and intonation
- Custom voice cloning for characters
- Streaming audio (plays while generating)

---

## Common Commands

### Voice Configuration

```bash
# Check current voice settings
python -m claude_code_voice config get voice

# Toggle voice input only
python -m claude_code_voice config set voice.input false

# Toggle voice output only
python -m claude_code_voice config set voice.output false

# Change push-to-talk key
python -m claude_code_voice config set voice.pushToTalkKey "Ctrl+Shift+V"

# List available characters
python -m claude_code_voice voice characters list

# Switch character
python -m claude_code_voice config set voice.selectedCharacter "none"  # disable character
python -m claude_code_voice config set voice.selectedCharacter "toudie"  # enable Toudie
```

### Audio Device Selection

```bash
# List available audio devices
python -m claude_code_voice voice devices list

# Set specific microphone
python -m claude_code_voice config set voice.audioDevices.inputDevice "Microphone (USB)"

# Set specific speaker
python -m claude_code_voice config set voice.audioDevices.outputDevice "Speakers (Realtek)"

# Reset to system default
python -m claude_code_voice config set voice.audioDevices.inputDevice null
```

---

## Example Voice Commands

### File Operations

- **"Read file main.ts"** - Opens and reads file content
- **"Create new file utils.ts"** - Creates empty file
- **"List all TypeScript files"** - Shows *.ts files
- **"Show current directory"** - Displays pwd

### Code Analysis

- **"Explain function getUserData"** - Describes function behavior
- **"Find all TODO comments"** - Searches codebase
- **"Check for errors in app.ts"** - Runs linter/type check

### Git Operations

- **"Show git status"** - Displays working tree status
- **"Create commit with message: add voice feature"** - Commits changes
- **"Show last 5 commits"** - Displays git log

---

## Troubleshooting

### Voice input not working

**Problem**: Pressing Ctrl+Space does nothing

**Solutions**:
1. Check microphone permissions:
   - **Windows**: Settings → Privacy → Microphone → Allow apps
   - **macOS**: System Preferences → Security & Privacy → Microphone
   - **Linux**: Check PulseAudio with `pactl list sources`

2. Test microphone:
   ```bash
   # Test system microphone
   python -m claude_code_voice voice test mic
   ```

3. Try different push-to-talk key:
   ```bash
   python -m claude_code_voice config set voice.pushToTalkKey "Ctrl+Shift+Space"
   ```

### Voice output not working

**Problem**: No audio playback

**Solutions**:
1. Check speaker/headphone connection

2. Test system TTS:
   ```bash
   # Test system text-to-speech
   python -m claude_code_voice voice test tts "Hello, this is a test"
   ```

3. Check audio output device:
   ```bash
   python -m claude_code_voice voice devices list
   ```

4. Try different output device or reset to default:
   ```bash
   python -m claude_code_voice config set voice.audioDevices.outputDevice null
   ```

### Poor voice recognition accuracy

**Problem**: Commands frequently misunderstood

**Solutions**:
1. Speak clearly and pause briefly before/after command

2. Use technical terms explicitly:
   - Say "package dot jay ess on" for `package.json`
   - Say "main dot tee ess" for `main.ts`

3. Optional: Add OpenAI Whisper as fallback (more accurate for technical terms):
   ```bash
   # Get OpenAI API key from platform.openai.com
   python -m claude_code_voice config set voice.apiKeys.openai "sk-..."
   python -m claude_code_voice config set voice.sttConfig.provider "whisper"  # force Whisper
   ```

### ElevenLabs voice quality issues

**Problem**: Choppy audio or slow response with ElevenLabs

**Solutions**:
1. Check API key is valid:
   ```bash
   python -m claude_code_voice voice test elevenlabs
   ```

2. Try faster model (lower quality but quicker):
   ```bash
   python -m claude_code_voice config set voice.ttsConfig.elevenlabsModel "eleven_turbo_v2"
   ```

3. Disable streaming if network is slow:
   ```bash
   python -m claude_code_voice config set voice.performance.ttsStreamingEnabled false
   ```

4. Fallback to system TTS temporarily:
   ```bash
   python -m claude_code_voice config set voice.ttsConfig.provider "system"
   ```

---

## Character Profiles

### Built-in Characters

#### Toudie (Gummy Bears)
- **Voice**: Cheerful, enthusiastic
- **Personality**: Helpful, occasionally references Gummi Berry juice
- **Activation**: `python -m claude_code_voice config set voice.selectedCharacter "toudie"`
- **Example**: *"Great gobs of gummiberries! Let me check that file for you!"*

### Creating Custom Characters

1. Create character profile JSON:
   ```json
   {
     "name": "my-character",
     "displayName": "My Character",
     "description": "Brief character description",
     "voiceId": "21m00Tcm4TlvDq8ikWAM",
     "voiceSettings": {
       "stability": 0.5,
       "similarityBoost": 0.75
     },
     "systemPrompt": "Transform responses like [character traits]...",
     "characteristicPhrases": [
       "Signature phrase 1",
       "Signature phrase 2"
     ],
     "transformationRules": {
       "addGreeting": true,
       "useCharacteristicPhrases": true,
       "preserveTechnicalContent": true
     }
   }
   ```

2. Save to `~/.claude-code/characters/my-character.json`

3. Activate:
   ```bash
   python -m claude_code_voice config set voice.selectedCharacter "my-character"
   ```

**Note**: Custom characters require ElevenLabs API key for full voice experience.

---

## Performance Tuning

### Reduce Latency

```bash
# Faster speech recognition (may reduce accuracy)
python -m claude_code_voice config set voice.sttConfig.timeout 2

# Faster TTS response
python -m claude_code_voice config set voice.ttsConfig.elevenlabsModel "eleven_turbo_v2"

# Enable streaming (play while generating)
python -m claude_code_voice config set voice.performance.ttsStreamingEnabled true
```

### Improve Accuracy

```bash
# Use Whisper for better technical term recognition (requires API key)
python -m claude_code_voice config set voice.sttConfig.provider "whisper"

# Use higher quality TTS model
python -m claude_code_voice config set voice.ttsConfig.elevenlabsModel "eleven_multilingual_v2"
```

---

## Cost Calculator

### Free Configuration (System Services)
- **STT**: Web Speech API - $0/month
- **TTS**: System TTS - $0/month
- **Total**: **$0/month** ✅

### Light Usage (30-100 commands/day)
- **STT**: Web Speech API - $0/month
- **TTS**: ElevenLabs Creator (30k chars) - $5/month
- **Total**: **$5/month**

### Regular Usage (100-300 commands/day)
- **STT**: Web Speech API - $0/month
- **TTS**: ElevenLabs Independent (100k chars) - $22/month
- **Total**: **$22/month**

### With Whisper Fallback
- **STT**: Whisper API (~4 min/month fallback) - $0-0.72/month
- **TTS**: Your choice
- **Add**: **$0-0.72/month**

---

## Configuration File Reference

Full configuration stored in `~/.claude-code/voice-config.json`:

```json
{
  "configVersion": 1,
  "voiceInputEnabled": true,
  "voiceOutputEnabled": true,
  "selectedCharacter": null,
  "pushToTalkKey": "Ctrl+Space",
  "audioDevices": {
    "inputDevice": null,
    "outputDevice": null
  },
  "apiKeys": {
    "openai": "",
    "elevenlabs": ""
  },
  "sttConfig": {
    "whisperModel": "whisper-1"
  },
  "ttsConfig": {
    "provider": "system",
    "elevenlabsModel": "eleven_multilingual_v2",
    "systemVoice": null
  },
  "performance": {
    "maxTranscriptionWaitSeconds": 3,
    "ttsStreamingEnabled": true
  }
}
```

---

## Next Steps

1. **Try basic commands** with free system TTS
2. **Test character roleplay** (works with system TTS too!)
3. **Optional**: Upgrade to ElevenLabs for premium quality
4. **Customize**: Create your own character profiles

## Support

- **Documentation**: [Full docs](../README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/claude-code-voice/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/claude-code-voice/discussions)

---

**Enjoy hands-free coding with Claude Code!** 🎤✨
