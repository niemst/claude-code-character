"""Voice output manager orchestrating TTS and audio playback."""

import time
from pathlib import Path
from typing import Callable, Optional

from src.audio.playback import AudioPlayer, PlaybackController
from src.config.persistence import load_config
from src.config.voice_config import TtsConfig, VoiceConfiguration
from src.hooks.output_hook import ClaudeCodeOutputHook
from src.voice.text_to_speech import TextToSpeech, TtsProvider
from src.voice.voice_session import VoiceSession


class VoiceOutputManager:
    """
    Manages the complete voice output workflow.

    Workflow:
    1. Claude Code produces text response
    2. Output hook intercepts response
    3. Convert text to speech via TTS
    4. Queue audio for playback
    5. Play audio through speakers
    6. Track statistics (playback latency)
    """

    def __init__(
        self,
        config: Optional[VoiceConfiguration] = None,
        session: Optional[VoiceSession] = None,
        on_playback_start: Optional[Callable[[], None]] = None,
        on_playback_stop: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize voice output manager.

        Args:
            config: Voice configuration (loads from file if not provided)
            session: Voice session for state tracking
            on_playback_start: Callback when playback starts
            on_playback_stop: Callback when playback stops
        """
        # Load configuration
        if config is None:
            config = load_config()
        self.config = config

        # Use provided session or create new one
        self.session = session if session is not None else VoiceSession()

        # Store callbacks
        self._on_playback_start_callback = on_playback_start
        self._on_playback_stop_callback = on_playback_stop

        # Initialize text-to-speech
        tts_provider = (
            TtsProvider.ELEVENLABS
            if self.config.tts_config.provider == "elevenlabs" and self.config.api_keys.elevenlabs
            else TtsProvider.SYSTEM
        )

        self.tts = TextToSpeech(
            elevenlabs_api_key=self.config.api_keys.elevenlabs,
            elevenlabs_model=self.config.tts_config.elevenlabs_model or "eleven_multilingual_v2",
            preferred_provider=tts_provider,
            system_voice=self.config.tts_config.system_voice,
        )

        # Initialize audio player
        self.player = AudioPlayer(
            on_playback_start=self._on_playback_start,
            on_playback_stop=self._on_playback_stop,
            device=self._get_output_device_id(),
        )

        # Initialize playback controller
        self.playback_controller = PlaybackController(
            player=self.player, on_queue_empty=self._on_queue_empty
        )

        # Initialize output hook
        self.output_hook = ClaudeCodeOutputHook(
            on_response=self._on_response_intercepted, debug=False
        )

        self._is_active = False
        self._response_timestamps: dict[str, int] = {}  # Track TTS start time

    def start(self) -> None:
        """Start voice output."""
        if self._is_active:
            print("⚠️  Voice output already active")
            return

        if not self.config.voice_output_enabled:
            print("⚠️  Voice output is disabled in configuration")
            return

        # Start playback controller
        self.playback_controller.start()

        # Start output hook monitoring
        self.output_hook.start_monitoring()

        self._is_active = True

        print("✅ Voice output started")
        print(f"   TTS providers: {[p.value for p in self.tts.get_available_providers()]}")
        print(f"   Playback enabled\n")

    def stop(self) -> None:
        """Stop voice output."""
        if not self._is_active:
            return

        # Stop output hook
        self.output_hook.stop_monitoring()

        # Stop playback controller
        self.playback_controller.stop()

        self._is_active = False

        print("✅ Voice output stopped")
        self._print_statistics()

    def speak(self, text: str, voice_id: Optional[str] = None) -> None:
        """
        Manually speak text (for testing).

        Args:
            text: Text to speak
            voice_id: Optional voice ID (for ElevenLabs)
        """
        if not self._is_active:
            print("⚠️  Voice output not active, call start() first")
            return

        self._process_response(text, voice_id)

    def interrupt(self) -> None:
        """Interrupt current playback."""
        if not self._is_active:
            return

        # Interrupt playback and measure latency
        latency_ms = self.playback_controller.interrupt()

        # Update statistics
        self.session.statistics.increment_interruptions(latency_ms)

        # Check performance criteria (SC-006: <500ms interrupt)
        if latency_ms > 500:
            print(f"⚠️  Interrupt slower than target (<500ms): {latency_ms}ms")
        else:
            print(f"✅ Interrupted playback ({latency_ms}ms)")

    def _on_response_intercepted(self, response_text: str) -> None:
        """
        Handle intercepted Claude Code response.

        Args:
            response_text: Response text from Claude Code
        """
        print(f"📥 Response intercepted: \"{response_text[:50]}...\"")
        self._process_response(response_text)

    def _process_response(self, text: str, voice_id: Optional[str] = None) -> None:
        """
        Process response text through TTS and queue for playback.

        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (for ElevenLabs)
        """
        # Track TTS start time
        tts_start = time.time()
        response_timestamp = int(tts_start * 1000)

        print("🔄 Synthesizing speech...")

        try:
            # Convert text to speech
            audio_data, provider_used, tts_duration_ms = self.tts.synthesize(
                text=text, voice_id=voice_id
            )

            print(f"✅ Synthesized ({provider_used.value})")
            print(f"   TTS time: {tts_duration_ms:.0f}ms")
            print(f"   Audio size: {len(audio_data)} bytes")

            # Calculate time from response to playback start
            playback_start_latency = int((time.time() - tts_start) * 1000)

            # Update statistics (SC-003: <1s playback start)
            self.session.statistics.update_playback_start_time(playback_start_latency)

            if playback_start_latency > 1000:
                print(
                    f"⚠️  Playback start slower than target (<1s): {playback_start_latency}ms"
                )

            # Queue for playback
            self.playback_controller.queue_audio(audio_data, "auto")

            # Queue response in session
            self.session.queue_response(
                text=text, timestamp=response_timestamp, character_transformed=False
            )

        except Exception as e:
            print(f"❌ TTS failed: {e}")

    def _on_playback_start(self) -> None:
        """Callback when playback starts."""
        # Set session state
        try:
            self.session.set_playing(True)
        except ValueError as e:
            print(f"⚠️  Cannot start playback: {e}")
            return

        print("🔊 Playback started...")

        if self._on_playback_start_callback:
            self._on_playback_start_callback()

    def _on_playback_stop(self) -> None:
        """Callback when playback stops."""
        # Reset session state
        self.session.set_playing(False)

        print("🔊 Playback stopped")

        # Dequeue response
        self.session.dequeue_response()

        if self._on_playback_stop_callback:
            self._on_playback_stop_callback()

    def _on_queue_empty(self) -> None:
        """Callback when playback queue becomes empty."""
        # All responses played
        pass

    def _get_output_device_id(self) -> Optional[int]:
        """
        Get output device ID from configuration.

        Returns:
            Device ID or None for default device
        """
        device_name = self.config.audio_devices.output_device
        if not device_name:
            return None

        # TODO: Map device name to device ID
        # For now, use default device
        return None

    def _print_statistics(self) -> None:
        """Print session statistics."""
        stats = self.session.statistics
        print("\n📊 Voice Output Statistics:")
        if stats.commands_issued_count > 0:
            print(f"   Average playback start time: {stats.average_playback_start_time_ms:.0f}ms")
        if stats.interruptions_count > 0:
            print(f"   Interruptions: {stats.interruptions_count}")
            print(f"   Average interrupt latency: {stats.average_interrupt_latency_ms:.0f}ms")

    @property
    def is_active(self) -> bool:
        """Check if voice output is active."""
        return self._is_active


def create_voice_output_manager(
    session: Optional[VoiceSession] = None,
) -> VoiceOutputManager:
    """
    Create and configure voice output manager.

    Args:
        session: Voice session for state tracking

    Returns:
        Configured VoiceOutputManager instance
    """
    return VoiceOutputManager(session=session)
