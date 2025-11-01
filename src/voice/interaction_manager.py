"""Voice interaction manager orchestrating push-to-talk, recording, and transcription."""

import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from src.audio.capture import PushToTalkHandler
from src.config.persistence import load_config
from src.config.voice_config import VoiceConfiguration
from src.voice.speech_to_text import SpeechToText, SttProvider
from src.voice.voice_session import LastCommand, VoiceSession


class VoiceInteractionManager:
    """
    Manages the complete voice input workflow.

    Workflow:
    1. User presses hotkey (Ctrl+Space by default)
    2. Start recording audio (isListening=True)
    3. User releases hotkey
    4. Stop recording (isListening=False)
    5. Transcribe audio to text
    6. Send text command to Claude Code
    7. Track statistics
    """

    def __init__(
        self,
        config: Optional[VoiceConfiguration] = None,
        on_command: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize voice interaction manager.

        Args:
            config: Voice configuration (loads from file if not provided)
            on_command: Callback when voice command is transcribed (receives command text)
        """
        # Load configuration
        if config is None:
            config = load_config()
        self.config = config

        # Callback for when command is ready
        self.on_command = on_command

        # Initialize voice session
        self.session = VoiceSession()

        # Initialize speech-to-text
        self.stt = SpeechToText(
            openai_api_key=self.config.api_keys.openai,
            whisper_model=self.config.stt_config.whisper_model,
            language="pl-PL",  # TODO: Make configurable
            max_wait_seconds=self.config.performance.max_transcription_wait_seconds,
        )

        # Initialize push-to-talk handler
        self.ptt_handler = PushToTalkHandler(
            hotkey=self.config.push_to_talk_key.lower().replace("+", "+"),
            on_audio_captured=self._on_audio_captured,
            sample_rate=16000,  # 16kHz for speech
            device=self._get_input_device_id(),
        )

        self._is_active = False

    def start(self) -> None:
        """Start voice interaction."""
        if self._is_active:
            print("⚠️  Voice interaction already active")
            return

        if not self.config.voice_input_enabled:
            print("⚠️  Voice input is disabled in configuration")
            return

        # Start push-to-talk handler
        self.ptt_handler.start()
        self._is_active = True

        print("✅ Voice interaction started")
        print(f"   Hotkey: {self.config.push_to_talk_key}")
        print(f"   STT providers: {[p.value for p in self.stt.get_available_providers()]}")
        print("\n💡 Press and hold Ctrl+Space to speak, release to send command\n")

    def stop(self) -> None:
        """Stop voice interaction."""
        if not self._is_active:
            return

        # Stop push-to-talk handler
        self.ptt_handler.stop()
        self._is_active = False

        print("✅ Voice interaction stopped")
        self._print_statistics()

    def _on_audio_captured(self, audio_data: np.ndarray, sample_rate: int) -> None:
        """
        Handle captured audio from push-to-talk.

        Args:
            audio_data: Recorded audio samples
            sample_rate: Audio sample rate
        """
        # Set session state
        try:
            self.session.set_listening(True)
        except ValueError as e:
            print(f"⚠️  Cannot start listening: {e}")
            return

        # Calculate audio duration
        audio_duration = len(audio_data) / sample_rate
        print(f"   Audio duration: {audio_duration:.1f}s")

        # Check minimum duration
        if audio_duration < 0.5:
            print("⚠️  Audio too short (minimum 0.5s)")
            self.session.set_listening(False)
            return

        # Transcribe audio
        print("🔄 Transcribing...")
        transcription_start = time.time()

        try:
            text, provider_used, duration_ms = self.stt.transcribe(audio_data, sample_rate)
            transcription_duration = int(duration_ms)

            print(f"✅ Transcribed ({provider_used.value}): \"{text}\"")
            print(f"   Transcription time: {transcription_duration}ms")

            # Update session with command
            timestamp = int(time.time() * 1000)
            self.session.last_command = LastCommand(
                spoken_text=text,
                transcribed_text=text,
                timestamp=timestamp,
                transcription_duration_ms=transcription_duration,
            )

            # Update statistics
            self.session.statistics.update_transcription_time(transcription_duration)

            # Check performance criteria (SC-002: <2s transcription)
            if transcription_duration > 2000:
                print(
                    f"⚠️  Transcription slower than target (<2s): {transcription_duration}ms"
                )

            # Send command to Claude Code
            if self.on_command:
                self.on_command(text)
            else:
                print(f"📝 Command: {text}")

        except Exception as e:
            print(f"❌ Transcription failed: {e}")

        finally:
            # Reset listening state
            self.session.set_listening(False)

    def _get_input_device_id(self) -> Optional[int]:
        """
        Get input device ID from configuration.

        Returns:
            Device ID or None for default device
        """
        device_name = self.config.audio_devices.input_device
        if not device_name:
            return None

        # TODO: Map device name to device ID
        # For now, use default device
        return None

    def _print_statistics(self) -> None:
        """Print session statistics."""
        stats = self.session.statistics
        print("\n📊 Session Statistics:")
        print(f"   Commands issued: {stats.commands_issued_count}")
        if stats.commands_issued_count > 0:
            print(f"   Average transcription time: {stats.average_transcription_time_ms:.0f}ms")

    @property
    def is_active(self) -> bool:
        """Check if voice interaction is active."""
        return self._is_active


def create_voice_interaction_manager(
    on_command: Optional[Callable[[str], None]] = None,
) -> VoiceInteractionManager:
    """
    Create and configure voice interaction manager.

    Args:
        on_command: Callback when voice command is transcribed

    Returns:
        Configured VoiceInteractionManager instance
    """
    return VoiceInteractionManager(on_command=on_command)
