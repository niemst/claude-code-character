"""Voice output manager orchestrating TTS and audio playback."""

import logging
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)

from src.audio.playback import AudioPlayer, PlaybackController
from src.character.transformer import CharacterTransformer
from src.config.persistence import load_config
from src.config.voice_config import VoiceConfiguration
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
        config: VoiceConfiguration | None = None,
        session: VoiceSession | None = None,
        on_playback_start: Callable[[], None] | None = None,
        on_playback_stop: Callable[[], None] | None = None,
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

        # Initialize character transformer
        self.character_transformer = CharacterTransformer(config=self.config)

        self._is_active = False
        self._response_timestamps: dict[str, int] = {}  # Track TTS start time

    def start(self) -> None:
        """Start voice output."""
        if self._is_active:
            logger.warning("Voice output already active")
            return

        if not self.config.voice_output_enabled:
            logger.warning("Voice output is disabled in configuration")
            return

        # Start playback controller
        self.playback_controller.start()

        # Start output hook monitoring
        self.output_hook.start_monitoring()

        self._is_active = True

        logger.info("Voice output started")
        logger.info("   TTS providers: %s", [p.value for p in self.tts.get_available_providers()])
        logger.info("   Playback enabled")

        # Show character status
        if self.character_transformer.is_active:
            logger.info("   Character: %s", self.character_transformer.character_name)
        else:
            logger.info("   Character: (none)")

    def stop(self) -> None:
        """Stop voice output."""
        if not self._is_active:
            return

        # Stop output hook
        self.output_hook.stop_monitoring()

        # Stop playback controller
        self.playback_controller.stop()

        self._is_active = False

        logger.info("Voice output stopped")
        self._print_statistics()

    def speak(self, text: str, voice_id: str | None = None) -> None:
        """
        Manually speak text (for testing).

        Args:
            text: Text to speak
            voice_id: Optional voice ID (for ElevenLabs)
        """
        if not self._is_active:
            logger.warning("Voice output not active, call start() first")
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
            logger.warning("Interrupt slower than target (<500ms): %dms", latency_ms)
        else:
            logger.info("Interrupted playback (%dms)", latency_ms)

    def _on_response_intercepted(self, response_text: str) -> None:
        """
        Handle intercepted Claude Code response.

        Args:
            response_text: Response text from Claude Code
        """
        logger.info('Response intercepted: "%s..."', response_text[:50])
        self._process_response(response_text)

    def _process_response(self, text: str, voice_id: str | None = None) -> None:
        """
        Process response text through TTS and queue for playback.

        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (for ElevenLabs)
        """
        # Track TTS start time
        tts_start = time.time()
        response_timestamp = int(tts_start * 1000)

        # Apply character transformation if active
        transformed_text, was_transformed = self.character_transformer.transform(text)
        character_transformed = was_transformed

        if was_transformed:
            logger.info(
                "Character transformation applied (%s)", self.character_transformer.character_name
            )

        # Get character-specific voice settings if available
        if voice_id is None:
            voice_settings = self.character_transformer.get_voice_settings()
            if voice_settings:
                voice_id, settings = voice_settings
                # Apply character voice settings to TTS
                self.tts.set_character_voice(
                    voice_id=voice_id,
                    stability=settings["stability"],
                    similarity_boost=settings["similarity_boost"],
                    style=settings.get("style"),
                    use_speaker_boost=settings.get("use_speaker_boost", True),
                )

        logger.info("Synthesizing speech...")

        try:
            # Convert text to speech
            audio_data, provider_used, tts_duration_ms = self.tts.synthesize(
                text=transformed_text, voice_id=voice_id
            )

            logger.info("Synthesized (%s)", provider_used.value)
            logger.info("   TTS time: %.0fms", tts_duration_ms)
            logger.info("   Audio size: %d bytes", len(audio_data))

            # Calculate time from response to playback start
            playback_start_latency = int((time.time() - tts_start) * 1000)

            # Update statistics (SC-003: <1s playback start)
            self.session.statistics.update_playback_start_time(playback_start_latency)

            if playback_start_latency > 1000:
                logger.warning(
                    "Playback start slower than target (<1s): %dms", playback_start_latency
                )

            # Queue for playback
            self.playback_controller.queue_audio(audio_data, "auto")

            # Queue response in session
            self.session.queue_response(
                text=transformed_text,
                timestamp=response_timestamp,
                character_transformed=character_transformed,
            )

        except Exception:
            logger.error("TTS failed", exc_info=True)

    def _on_playback_start(self) -> None:
        """Callback when playback starts."""
        # Set session state
        try:
            self.session.set_playing(True)
        except ValueError as e:
            logger.warning("Cannot start playback: %s", e)
            return

        logger.info("Playback started")

        if self._on_playback_start_callback:
            self._on_playback_start_callback()

    def _on_playback_stop(self) -> None:
        """Callback when playback stops."""
        # Reset session state
        self.session.set_playing(False)

        logger.info("Playback stopped")

        # Dequeue response
        self.session.dequeue_response()

        if self._on_playback_stop_callback:
            self._on_playback_stop_callback()

    def _on_queue_empty(self) -> None:
        """Callback when playback queue becomes empty."""
        # All responses played
        pass

    def _get_output_device_id(self) -> int | None:
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
        logger.info("Voice Output Statistics:")
        if stats.commands_issued_count > 0:
            logger.info("   Average playback start time: %.0fms", stats.average_playback_start_time_ms)
        if stats.interruptions_count > 0:
            logger.info("   Interruptions: %d", stats.interruptions_count)
            logger.info("   Average interrupt latency: %.0fms", stats.average_interrupt_latency_ms)

    @property
    def is_active(self) -> bool:
        """Check if voice output is active."""
        return self._is_active


def create_voice_output_manager(
    session: VoiceSession | None = None,
) -> VoiceOutputManager:
    """
    Create and configure voice output manager.

    Args:
        session: Voice session for state tracking

    Returns:
        Configured VoiceOutputManager instance
    """
    return VoiceOutputManager(session=session)
