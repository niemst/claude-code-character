# Claude Code Character - Voice-Enabled Interaction

Voice-enabled character interaction for Claude Code. Control Claude Code with your voice and optionally add character personality to responses.

## Features

### User Story 1 - Voice Command Input

- **Push-to-talk voice commands** - Press and hold Ctrl+Space, speak your command, release to execute
- **Free speech recognition** - Uses Google Web Speech API (no API key required)
- **Automatic fallback** - Falls back to OpenAI Whisper if Web Speech API unavailable
- **Performance tracking** - Monitors transcription latency (target: <2s)
- **Cross-platform** - Works on Windows, macOS, and Linux

### User Story 2 - Voice Response Output

- **Text-to-speech** - System TTS (free) or ElevenLabs (premium quality)
- **Automatic provider selection** - Uses best available TTS provider
- **Audio playback** - Plays responses through speakers/headphones
- **Streaming support** - Start playback while receiving audio (ElevenLabs)
- **Interrupt handling** - Stop playback by pressing Ctrl+Space (target: <500ms)
- **Performance monitoring** - Tracks playback start latency (target: <1s)

### User Story 3 - Character Roleplay

- **Character personalities** - Add personality to voice responses (e.g., like Toudie from Gummy Bears)
- **Technical content preservation** - 100% accuracy for code, paths, errors
- **Characteristic phrases** - Inject character-specific catchphrases
- **Character-specific voices** - Use custom ElevenLabs voice per character
- **Easy character switching** - Select character via CLI

## Requirements

- **Python 3.11+**
- **Audio devices** - Microphone for voice input (speakers/headphones for voice output when implemented)
- **Operating System** - Windows, macOS, or Linux

## Installation

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone repository

```bash
git clone <repository-url>
cd claude-code-character
```

### 3. Install dependencies

```bash
# Install core dependencies (free, no API keys required)
uv pip install -e .

# Optional: Install premium features (requires API keys)
uv pip install -e ".[premium]"
```

## Quick Start

### 1. Initialize configuration

```bash
python -m src config init
```

This creates `~/.claude-code/voice-config.json` with default settings.

### 2. Enable voice input and output

```bash
python -m src config enable-voice-input
python -m src config enable-voice-output
```

### 3. Test your microphone and speakers

```bash
python -m src list-devices
```

This shows all available audio devices. The default device is used automatically.

### 4. Test speech-to-text and text-to-speech

```bash
# Test STT (speech input)
python -m src test-stt

# Test TTS (speech output)
python -m src test-tts
```

Press Ctrl+Space, speak a test phrase, and release. You should see the transcription and hear the response.

### 5. (Optional) Select character for roleplay

```bash
# List available characters
python -m src list-characters

# Select Toudie
python -m src select-character toudie

# Or disable character
python -m src select-character none
```

### 6. Start voice interaction

```bash
python -m src start
```

Now you can control Claude Code with voice commands:

1. **Press and hold** Ctrl+Space
2. **Speak** your command (e.g., "read file main.py")
3. **Release** Ctrl+Space
4. The command is transcribed and sent to Claude Code
5. **Hear** the response with optional character personality

Press Ctrl+C to stop.

## Configuration

### View current configuration

```bash
python -m src config show
```

### Configuration file location

- **Linux/macOS**: `~/.claude-code/voice-config.json`
- **Windows**: `%USERPROFILE%\.claude-code\voice-config.json`

### Configuration options

```json
{
  "config_version": 1,
  "voice_input_enabled": true,
  "voice_output_enabled": false,
  "selected_character": null,
  "push_to_talk_key": "Ctrl+Space",
  "audio_devices": {
    "input_device": null,
    "output_device": null
  },
  "api_keys": {
    "openai": "",
    "elevenlabs": ""
  },
  "stt_config": {
    "whisper_model": "whisper-1"
  },
  "tts_config": {
    "provider": "system",
    "elevenlabs_model": "eleven_multilingual_v2",
    "system_voice": null
  },
  "performance": {
    "max_transcription_wait_seconds": 3,
    "tts_streaming_enabled": true
  }
}
```

### Add API keys (optional)

Edit `~/.claude-code/voice-config.json` and add your API keys:

```json
{
  "api_keys": {
    "openai": "sk-...",
    "elevenlabs": "..."
  }
}
```

Or set environment variables (recommended for security):

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-..."
export ELEVENLABS_API_KEY="..."

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."
$env:ELEVENLABS_API_KEY="..."
```

**Note**: Environment variables override config file values. API keys are optional - the system works with free services by default:
- **STT**: Google Web Speech API (free) → OpenAI Whisper (paid, if key provided)
- **TTS**: System TTS (free) → ElevenLabs (paid, if key provided)

## CLI Reference

### Main commands

```bash
# Start voice interaction
python -m src start

# Configuration
python -m src config show                    # Show current configuration
python -m src config init [--force]         # Initialize default configuration
python -m src config enable-voice-input     # Enable voice input
python -m src config disable-voice-input    # Disable voice input
python -m src config enable-voice-output    # Enable voice output
python -m src config disable-voice-output   # Disable voice output

# Device management
python -m src list-devices                  # List audio devices
python -m src list-characters               # List available characters

# Character management
python -m src select-character <name>       # Select character for roleplay
python -m src select-character none         # Disable character

# Testing
python -m src test-stt                      # Test speech-to-text
python -m src test-tts                      # Test text-to-speech
```

## Usage Examples

### Example 1: Basic voice command

```
User: [Press Ctrl+Space]
User: "read file main dot py"
User: [Release Ctrl+Space]

System: Recording started...
System: Recording stopped
System: Transcribing...
System: Transcribed (web_speech_api): "read file main.py"
System:    Transcription time: 847ms

Claude Code: [executes command]
```

### Example 2: File operation

```
User: [Ctrl+Space] "create a new file called utils dot py" [Release]

System: Transcribed: "create a new file called utils.py"

Claude Code: [creates utils.py]
```

### Example 3: Code generation

```
User: [Ctrl+Space] "write a function to calculate fibonacci numbers" [Release]

System: Transcribed: "write a function to calculate fibonacci numbers"

Claude Code: [generates fibonacci function]
```

## Troubleshooting

### "sounddevice not available"

Install PortAudio library:

```bash
# macOS
brew install portaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev

# Windows
# PortAudio is included with sounddevice wheel
```

Then reinstall sounddevice:

```bash
uv pip install --force-reinstall sounddevice
```

### "SpeechRecognition library not available"

```bash
uv pip install SpeechRecognition
```

### Microphone not working

1. Check available devices: `python -m src list-devices`
2. Ensure your microphone is not muted
3. Grant microphone permissions (macOS: System Preferences → Security & Privacy → Microphone)
4. Test with system voice recorder first

### Transcription fails

1. Check internet connection (Web Speech API requires internet)
2. Try adding OpenAI API key for Whisper fallback
3. Ensure you're speaking clearly and loudly enough
4. Check microphone audio levels in system settings

### "Cannot start listening while playing"

This is expected - you cannot speak commands while Claude Code is playing a voice response. Wait for the response to finish, or press Ctrl+Space to interrupt.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Voice Interaction                       │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────┐ │
│  │ Push-to-Talk │──▶│ Audio Capture│──▶│ Speech-to-Text│ │
│  │   (pynput)   │   │ (sounddevice)│   │(Web Speech API)│ │
│  └──────────────┘   └──────────────┘   └───────────────┘ │
│                                                ▼            │
│                                          ┌──────────────┐  │
│                                          │  Input Hook  │  │
│                                          │ (to Claude)  │  │
│                                          └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Development

### Pre-commit Hooks

This project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

Hooks include:
- **black** - Code formatting (PEP 8, 100 char lines)
- **ruff** - Fast Python linter with auto-fix
- **mypy** - Static type checking
- **detect-secrets** - Prevents committing secrets
- Standard checks (trailing whitespace, JSON formatting, etc.)

### Manual Code Quality Checks

```bash
# Format with black
black src/ --line-length 100

# Lint with ruff
ruff check src/ --fix

# Type check with mypy
mypy src/ --ignore-missing-imports
```

### Project structure

```
claude-code-character/
├── src/
│   ├── audio/               # Audio capture and playback
│   │   ├── capture.py       # Push-to-talk and recording
│   │   ├── playback.py      # Audio playback and streaming
│   │   └── device_manager.py
│   ├── voice/               # Voice processing
│   │   ├── speech_to_text.py
│   │   ├── text_to_speech.py
│   │   ├── voice_session.py
│   │   ├── interaction_manager.py
│   │   └── output_manager.py
│   ├── character/           # Character profiles
│   │   ├── profile.py
│   │   ├── transformer.py   # Text transformation with personality
│   │   └── profiles/
│   │       └── toudie.json
│   ├── config/              # Configuration
│   │   ├── voice_config.py
│   │   └── persistence.py
│   ├── hooks/               # Claude Code integration
│   │   ├── input_hook.py
│   │   └── output_hook.py
│   ├── cli.py               # Command-line interface
│   └── __main__.py          # Entry point
├── specs/                   # Design documents
│   └── 001-voice-character-interaction/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── ...
├── pyproject.toml
└── README.md
```

## Success Criteria

- [x] **SC-001**: 80% of common commands successful via voice
- [x] **SC-002**: Voice command recognition <2 seconds
- [x] **SC-003**: Voice playback starts <1 second
- [x] **SC-004**: Character roleplay maintains 100% technical accuracy
- [ ] SC-005: Complete 15+ minute coding session using only voice
- [x] **SC-006**: Voice interruption responds <500ms
- [x] **SC-007**: Character personality in 90%+ of responses (when enabled)
- [ ] SC-008: Voice toggle in <3 seconds

## Roadmap

### Phase 3: User Story 1 - Complete

- [x] Push-to-talk voice command input
- [x] Web Speech API + Whisper fallback STT
- [x] Performance monitoring
- [x] Input hook to Claude Code

### Phase 4: User Story 2 - Complete

- [x] Text-to-speech output
- [x] System TTS + ElevenLabs support
- [x] Audio playback and streaming
- [x] Output hook from Claude Code
- [x] Interrupt handling
- [x] Performance monitoring

### Phase 5: User Story 3 - Complete

- [x] Character profile system
- [x] Text transformation (personality injection)
- [x] Technical content preservation
- [x] Character-specific voice settings
- [x] CLI character selection

### Phase 6: Polish - Complete

- [x] Environment variable support for API keys
- [x] Graceful degradation for missing devices
- [x] Example configuration file
- [x] Code formatting (black)
- [x] Pre-commit hooks (ruff, mypy, detect-secrets)
- [x] Comprehensive documentation

## License

This project is distributed under a **Custom License** based on [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/),
with additional restrictions prohibiting any AI/LLM training, commercial use, or code modification.
No warranty of any kind is provided.
See the full license text here: [LICENSE](./LICENSE)
