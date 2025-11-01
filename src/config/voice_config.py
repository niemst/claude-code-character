"""Voice configuration data structures and defaults."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AudioDevices:
    """Audio input/output device configuration."""

    input_device: str | None = None
    output_device: str | None = None


@dataclass
class ApiKeys:
    """API keys for external services."""

    openai: str = ""
    elevenlabs: str = ""


@dataclass
class SttConfig:
    """Speech-to-text configuration."""

    whisper_model: Literal["whisper-1"] = "whisper-1"


@dataclass
class TtsConfig:
    """Text-to-speech configuration."""

    provider: Literal["system", "elevenlabs"] = "system"
    elevenlabs_model: Literal["eleven_multilingual_v2", "eleven_turbo_v2"] | None = (
        "eleven_multilingual_v2"
    )
    system_voice: str | None = None


@dataclass
class Performance:
    """Performance-related settings."""

    max_transcription_wait_seconds: int = 3
    tts_streaming_enabled: bool = True


@dataclass
class VoiceConfiguration:
    """Complete voice configuration for Claude Code."""

    config_version: int = 1
    voice_input_enabled: bool = False
    voice_output_enabled: bool = False
    selected_character: str | None = None
    push_to_talk_key: str = "Ctrl+Space"
    audio_devices: AudioDevices = field(default_factory=AudioDevices)
    api_keys: ApiKeys = field(default_factory=ApiKeys)
    stt_config: SttConfig = field(default_factory=SttConfig)
    tts_config: TtsConfig = field(default_factory=TtsConfig)
    performance: Performance = field(default_factory=Performance)


def create_default_config() -> VoiceConfiguration:
    """Create a VoiceConfiguration with sensible defaults."""
    return VoiceConfiguration()
