#!/usr/bin/env python3
"""
Stop hook for Claude Code that reads assistant responses and plays them as voice.

This script is invoked by Claude Code as a Stop hook. It receives JSON via stdin,
reads the transcript, extracts the last assistant message, transforms it through
character roleplay, and plays it as synthesized speech.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def read_transcript(transcript_path: str) -> list[dict[str, Any]]:
    """
    Read JSONL transcript file.

    Args:
        transcript_path: Absolute path to JSONL transcript file

    Returns:
        List of message dictionaries
    """
    path = Path(transcript_path).expanduser()

    if not path.exists():
        logger.error("Transcript file not found: %s", path)
        return []

    messages = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))
        return messages
    except Exception:
        logger.error("Failed to read transcript", exc_info=True)
        return []


def extract_last_assistant_message(messages: list[dict[str, Any]]) -> str | None:
    """
    Extract text from the last assistant message.

    Args:
        messages: List of message dictionaries from transcript

    Returns:
        Concatenated text from last assistant message, or None if not found
    """
    for message in reversed(messages):
        if message.get("role") == "assistant":
            content = message.get("content", [])

            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))

            if text_parts:
                return "\n".join(text_parts)

    return None


def transform_text(text: str, character_name: str = "toadwart") -> str:
    """
    Transform text through character transformer.

    Args:
        text: Original assistant message text
        character_name: Name of character profile to use

    Returns:
        Transformed text with character personality, or original if transformation fails
    """
    try:
        from src.character.profile import load_character_profile
        from src.character.transformer import CharacterTransformer

        profile_path = (
            Path(__file__).parent.parent / "character" / "profiles" / f"{character_name}.json"
        )

        if not profile_path.exists():
            logger.warning("Character profile not found: %s, using original text", profile_path)
            return text

        profile = load_character_profile(profile_path)
        transformer = CharacterTransformer(profile)

        transformed, _success = transformer.transform(text)
        return transformed

    except Exception:
        logger.error("Character transformation failed, using original text", exc_info=True)
        return text


def play_speech(text: str, character_name: str = "toadwart") -> None:
    """
    Synthesize and play speech.

    Args:
        text: Text to synthesize and play
        character_name: Character profile to use for voice settings
    """
    try:
        from src.audio.playback import AudioPlayer, PlaybackController
        from src.character.profile import load_character_profile
        from src.config.persistence import load_config
        from src.voice.text_to_speech import TextToSpeech, TtsProvider

        config = load_config()

        logger.info("API key loaded: %s", "YES" if config.api_keys.elevenlabs else "NO")
        logger.info(
            "API key length: %d",
            len(config.api_keys.elevenlabs) if config.api_keys.elevenlabs else 0,
        )

        profile_path = (
            Path(__file__).parent.parent / "character" / "profiles" / f"{character_name}.json"
        )
        if profile_path.exists():
            profile = load_character_profile(profile_path)
            voice_id = profile.voice_id
            voice_stability = profile.voice_settings.stability
            voice_similarity = profile.voice_settings.similarity_boost
        else:
            voice_id = "21m00Tcm4TlvDq8ikWAM"
            voice_stability = 0.5
            voice_similarity = 0.75

        tts = TextToSpeech(
            elevenlabs_api_key=config.api_keys.elevenlabs,
            default_voice_id=voice_id,
            elevenlabs_model=config.tts_config.elevenlabs_model or "eleven_turbo_v2",
            preferred_provider=TtsProvider.ELEVENLABS,
            voice_stability=voice_stability,
            voice_similarity_boost=voice_similarity,
        )

        player = AudioPlayer()
        playback = PlaybackController(player=player)

        playback.start()

        logger.info("Synthesizing speech...")

        # Use non-streaming synthesis to get complete audio
        audio_data, provider_used, duration_ms = tts.synthesize(text)
        logger.info("Synthesis completed in %dms using %s", duration_ms, provider_used.value)

        # Determine audio format based on provider
        from src.voice.text_to_speech import TtsProvider

        audio_format = "mp3" if provider_used == TtsProvider.ELEVENLABS else "wav"

        playback.queue_audio(audio_data, audio_format)

        time.sleep(2)

        playback.stop()

        logger.info("Speech playback completed")

    except Exception:
        logger.error("Speech synthesis failed", exc_info=True)
        raise


def main() -> int:
    """
    Main hook entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    start_time = time.time()

    try:
        hook_input = json.load(sys.stdin)

        transcript_path = hook_input.get("transcript_path")
        if not transcript_path:
            logger.error("No transcript_path in hook input")
            return 1

        logger.info("Reading transcript: %s", transcript_path)
        messages = read_transcript(transcript_path)

        if not messages:
            logger.warning("No messages in transcript")
            return 0

        assistant_text = extract_last_assistant_message(messages)

        if not assistant_text:
            logger.warning("No assistant message found in transcript")
            return 0

        if len(assistant_text.strip()) < 5:
            logger.info("Assistant message too short, skipping TTS")
            return 0

        elapsed = time.time() - start_time
        if len(assistant_text) > 3000:
            logger.info("Message too long (%d chars), skipping transformation", len(assistant_text))
            transformed_text = assistant_text
        elif elapsed > 25:
            logger.warning("Timeout approaching (%.1fs elapsed), skipping transformation", elapsed)
            transformed_text = assistant_text
        else:
            logger.info("Transforming text through character...")
            transformed_text = transform_text(assistant_text)

        play_speech(transformed_text, character_name="toadwart")

        return 0

    except Exception:
        logger.error("Hook execution failed", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
