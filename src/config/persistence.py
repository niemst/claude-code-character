"""Configuration persistence - load and save voice configuration."""

import json
import os
from pathlib import Path
from typing import Any

from src.config.voice_config import (
    ApiKeys,
    AudioDevices,
    Performance,
    SttConfig,
    TtsConfig,
    VoiceConfiguration,
    create_default_config,
)


def get_project_root() -> Path:
    """Get the project root directory by finding pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback to current working directory if pyproject.toml not found
    return Path.cwd()


def get_config_path() -> Path:
    """Get the path to the voice configuration file."""
    project_root = get_project_root()
    config_dir = project_root / ".claude"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "voice-config.json"


def load_config() -> VoiceConfiguration:
    """
    Load voice configuration from .claude/voice-config.json in the project root.

    API keys can be overridden by environment variables:
    - OPENAI_API_KEY
    - ELEVENLABS_API_KEY
    """
    config_path = get_config_path()

    if not config_path.exists():
        config = create_default_config()
    else:
        try:
            with open(config_path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            config = VoiceConfiguration(
                config_version=data.get("config_version", 1),
                voice_input_enabled=data.get("voice_input_enabled", False),
                voice_output_enabled=data.get("voice_output_enabled", False),
                selected_character=data.get("selected_character"),
                push_to_talk_key=data.get("push_to_talk_key", "Ctrl+Space"),
                audio_devices=AudioDevices(
                    input_device=data.get("audio_devices", {}).get("input_device"),
                    output_device=data.get("audio_devices", {}).get("output_device"),
                ),
                api_keys=ApiKeys(
                    openai=data.get("api_keys", {}).get("openai", ""),
                    elevenlabs=data.get("api_keys", {}).get("elevenlabs", ""),
                ),
                stt_config=SttConfig(
                    whisper_model=data.get("stt_config", {}).get("whisper_model", "whisper-1")
                ),
                tts_config=TtsConfig(
                    provider=data.get("tts_config", {}).get("provider", "system"),
                    elevenlabs_model=data.get("tts_config", {}).get("elevenlabs_model"),
                    system_voice=data.get("tts_config", {}).get("system_voice"),
                ),
                performance=Performance(
                    max_transcription_wait_seconds=data.get("performance", {}).get(
                        "max_transcription_wait_seconds", 3
                    ),
                    tts_streaming_enabled=data.get("performance", {}).get(
                        "tts_streaming_enabled", True
                    ),
                ),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration instead")
            config = create_default_config()

    # Override API keys from environment variables if set
    openai_env = os.getenv("OPENAI_API_KEY")
    if openai_env:
        config.api_keys.openai = openai_env

    elevenlabs_env = os.getenv("ELEVENLABS_API_KEY")
    if elevenlabs_env:
        config.api_keys.elevenlabs = elevenlabs_env

    return config


def save_config(config: VoiceConfiguration) -> None:
    """Save voice configuration to .claude/voice-config.json in the project root with chmod 600."""
    config_path = get_config_path()

    data = {
        "config_version": config.config_version,
        "voice_input_enabled": config.voice_input_enabled,
        "voice_output_enabled": config.voice_output_enabled,
        "selected_character": config.selected_character,
        "push_to_talk_key": config.push_to_talk_key,
        "audio_devices": {
            "input_device": config.audio_devices.input_device,
            "output_device": config.audio_devices.output_device,
        },
        "api_keys": {
            "openai": config.api_keys.openai,
            "elevenlabs": config.api_keys.elevenlabs,
        },
        "stt_config": {"whisper_model": config.stt_config.whisper_model},
        "tts_config": {
            "provider": config.tts_config.provider,
            "elevenlabs_model": config.tts_config.elevenlabs_model,
            "system_voice": config.tts_config.system_voice,
        },
        "performance": {
            "max_transcription_wait_seconds": config.performance.max_transcription_wait_seconds,
            "tts_streaming_enabled": config.performance.tts_streaming_enabled,
        },
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Set file permissions to 600 (owner read/write only) on Unix systems
    if os.name != "nt":  # Not Windows
        os.chmod(config_path, 0o600)
