"""Text-to-speech synthesis with multiple provider support."""

import logging
import time
from collections.abc import Generator
from enum import Enum

logger = logging.getLogger(__name__)

try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from elevenlabs import Voice, VoiceSettings, generate

    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False


class TtsProvider(Enum):
    """Available text-to-speech providers."""

    SYSTEM = "system"  # System TTS via pyttsx3 (free)
    ELEVENLABS = "elevenlabs"  # ElevenLabs API (paid)


class TtsError(Exception):
    """Base exception for text-to-speech errors."""

    pass


class TtsNetworkError(TtsError):
    """Network error during TTS."""

    pass


class TtsApiError(TtsError):
    """API error during TTS."""

    pass


def synthesize_with_system_tts(
    text: str, voice: str | None = None, rate: int = 150, volume: float = 0.9
) -> bytes:
    """
    Synthesize speech using system TTS (pyttsx3).

    Args:
        text: Text to synthesize
        voice: Voice ID (None for default)
        rate: Speech rate (words per minute)
        volume: Volume level (0.0 to 1.0)

    Returns:
        Audio data as WAV bytes

    Raises:
        TtsError: If synthesis fails
    """
    if not PYTTSX3_AVAILABLE:
        raise TtsError("pyttsx3 library not available")

    try:
        engine = pyttsx3.init()

        # Set properties
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)

        if voice:
            engine.setProperty("voice", voice)

        # Save to memory buffer
        # Note: pyttsx3 doesn't support direct audio output to bytes
        # We'll use a temporary file approach
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        engine.save_to_file(text, tmp_path)
        engine.runAndWait()

        # Read back the WAV file
        with open(tmp_path, "rb") as f:
            audio_data = f.read()

        # Clean up temp file
        import os

        os.unlink(tmp_path)

        return audio_data

    except Exception as e:
        raise TtsError(f"System TTS error: {e}") from e


def synthesize_with_elevenlabs(
    text: str,
    api_key: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default: Rachel voice
    model: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float | None = None,
    use_speaker_boost: bool = True,
) -> bytes:
    """
    Synthesize speech using ElevenLabs API.

    Args:
        text: Text to synthesize
        api_key: ElevenLabs API key
        voice_id: Voice ID from ElevenLabs
        model: Model to use
        stability: Voice stability (0.0 to 1.0)
        similarity_boost: Voice similarity boost (0.0 to 1.0)
        style: Style exaggeration (0.0 to 1.0, optional)
        use_speaker_boost: Enable speaker boost

    Returns:
        Audio data as MP3 bytes

    Raises:
        TtsError: If synthesis fails
    """
    if not ELEVENLABS_AVAILABLE:
        raise TtsError("elevenlabs library not available")

    if not api_key:
        raise TtsError("ElevenLabs API key not provided")

    try:
        # Configure voice with settings
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style if style is not None else 0.0,
            use_speaker_boost=use_speaker_boost,
        )

        voice = Voice(
            voice_id=voice_id,
            settings=voice_settings,
        )

        # Generate audio (without streaming, returns bytes directly)
        audio_data = generate(
            text=text,
            voice=voice,
            model=model,
            api_key=api_key,
        )

        # Check if it's already bytes or needs to be collected from generator
        if isinstance(audio_data, bytes):
            return audio_data
        else:
            # It's a generator, collect chunks
            audio_chunks = []
            for chunk in audio_data:
                if chunk and isinstance(chunk, bytes):
                    audio_chunks.append(chunk)
            return b"".join(audio_chunks)

    except Exception as e:
        error_msg = str(e).lower()
        if "network" in error_msg or "connection" in error_msg:
            raise TtsNetworkError(f"ElevenLabs network error: {e}") from e
        elif "api" in error_msg or "quota" in error_msg or "authentication" in error_msg:
            raise TtsApiError(f"ElevenLabs API error: {e}") from e
        else:
            raise TtsError(f"ElevenLabs error: {e}") from e


def synthesize_with_elevenlabs_streaming(
    text: str,
    api_key: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float | None = None,
    use_speaker_boost: bool = True,
) -> Generator[bytes, None, None]:
    """
    Synthesize speech using ElevenLabs API with streaming.

    Args:
        text: Text to synthesize
        api_key: ElevenLabs API key
        voice_id: Voice ID from ElevenLabs
        model: Model to use
        stability: Voice stability (0.0 to 1.0)
        similarity_boost: Voice similarity boost (0.0 to 1.0)
        style: Style exaggeration (0.0 to 1.0, optional)
        use_speaker_boost: Enable speaker boost

    Yields:
        Audio chunks as bytes

    Raises:
        TtsError: If synthesis fails
    """
    if not ELEVENLABS_AVAILABLE:
        raise TtsError("elevenlabs library not available")

    if not api_key:
        raise TtsError("ElevenLabs API key not provided")

    try:
        # Configure voice with settings
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style if style is not None else 0.0,
            use_speaker_boost=use_speaker_boost,
        )

        voice = Voice(
            voice_id=voice_id,
            settings=voice_settings,
        )

        # Generate audio with streaming
        audio_stream = generate(
            text=text,
            voice=voice,
            model=model,
            api_key=api_key,
            stream=True,
        )

        # Yield chunks as they arrive
        for chunk in audio_stream:
            if chunk:
                yield chunk

    except Exception as e:
        error_msg = str(e).lower()
        if "network" in error_msg or "connection" in error_msg:
            raise TtsNetworkError(f"ElevenLabs network error: {e}") from e
        elif "api" in error_msg or "quota" in error_msg or "authentication" in error_msg:
            raise TtsApiError(f"ElevenLabs API error: {e}") from e
        else:
            raise TtsError(f"ElevenLabs error: {e}") from e


class TextToSpeech:
    """
    Text-to-speech synthesis with automatic provider fallback.

    Implements the following fallback chain:
    1. ElevenLabs API - Premium quality, character voices (if API key provided)
    2. System TTS - Free, cross-platform fallback
    """

    def __init__(
        self,
        elevenlabs_api_key: str = "",
        default_voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        elevenlabs_model: str = "eleven_multilingual_v2",
        preferred_provider: TtsProvider = TtsProvider.SYSTEM,
        voice_stability: float = 0.5,
        voice_similarity_boost: float = 0.75,
        voice_style: float | None = None,
        use_speaker_boost: bool = True,
        system_voice: str | None = None,
        system_rate: int = 150,
    ) -> None:
        """
        Initialize text-to-speech synthesizer.

        Args:
            elevenlabs_api_key: ElevenLabs API key (optional)
            default_voice_id: Default ElevenLabs voice ID
            elevenlabs_model: ElevenLabs model to use
            preferred_provider: Preferred TTS provider
            voice_stability: Voice stability for ElevenLabs
            voice_similarity_boost: Voice similarity boost for ElevenLabs
            voice_style: Voice style for ElevenLabs
            use_speaker_boost: Use speaker boost for ElevenLabs
            system_voice: System TTS voice (optional)
            system_rate: System TTS speech rate
        """
        self.elevenlabs_api_key = elevenlabs_api_key
        self.default_voice_id = default_voice_id
        self.elevenlabs_model = elevenlabs_model
        self.preferred_provider = preferred_provider
        self.voice_stability = voice_stability
        self.voice_similarity_boost = voice_similarity_boost
        self.voice_style = voice_style
        self.use_speaker_boost = use_speaker_boost
        self.system_voice = system_voice
        self.system_rate = system_rate

        # Determine available providers
        self.available_providers: list[TtsProvider] = []
        if PYTTSX3_AVAILABLE:
            self.available_providers.append(TtsProvider.SYSTEM)
        if ELEVENLABS_AVAILABLE and elevenlabs_api_key:
            self.available_providers.append(TtsProvider.ELEVENLABS)

    def synthesize(
        self, text: str, voice_id: str | None = None, streaming: bool = False
    ) -> tuple[bytes, TtsProvider, float]:
        """
        Synthesize text to speech using available providers with automatic fallback.

        Args:
            text: Text to synthesize
            voice_id: Voice ID (for ElevenLabs, overrides default)
            streaming: Use streaming if available (ElevenLabs only)

        Returns:
            Tuple of (audio_data, provider_used, duration_ms)

        Raises:
            TtsError: If all providers fail
        """
        if not self.available_providers:
            raise TtsError(
                "No TTS providers available. Install pyttsx3 or provide ElevenLabs API key."
            )

        if not text or not text.strip():
            raise TtsError("Empty text provided")

        # Determine provider order
        providers = self._get_provider_order()

        last_error: Exception | None = None
        start_time = time.time()

        for provider in providers:
            try:
                if provider == TtsProvider.ELEVENLABS:
                    voice = voice_id or self.default_voice_id
                    audio_data = synthesize_with_elevenlabs(
                        text=text,
                        api_key=self.elevenlabs_api_key,
                        voice_id=voice,
                        model=self.elevenlabs_model,
                        stability=self.voice_stability,
                        similarity_boost=self.voice_similarity_boost,
                        style=self.voice_style,
                        use_speaker_boost=self.use_speaker_boost,
                    )
                    duration_ms = (time.time() - start_time) * 1000
                    return (audio_data, provider, duration_ms)

                elif provider == TtsProvider.SYSTEM:
                    audio_data = synthesize_with_system_tts(
                        text=text, voice=self.system_voice, rate=self.system_rate
                    )
                    duration_ms = (time.time() - start_time) * 1000
                    return (audio_data, provider, duration_ms)

            except (TtsNetworkError, TtsApiError, TtsError) as e:
                last_error = e
                logger.warning("%s failed: %s, trying next provider", provider.value, e)
                continue

        # All providers failed
        duration_ms = (time.time() - start_time) * 1000
        raise TtsError(
            f"All TTS providers failed. Last error: {last_error}. Duration: {duration_ms:.0f}ms"
        )

    def synthesize_streaming(
        self, text: str, voice_id: str | None = None
    ) -> Generator[bytes, None, None]:
        """
        Synthesize text to speech with streaming (ElevenLabs only).

        Args:
            text: Text to synthesize
            voice_id: Voice ID (overrides default)

        Yields:
            Audio chunks as bytes

        Raises:
            TtsError: If streaming not available or fails
        """
        if TtsProvider.ELEVENLABS not in self.available_providers:
            raise TtsError("Streaming TTS requires ElevenLabs API key")

        voice = voice_id or self.default_voice_id

        yield from synthesize_with_elevenlabs_streaming(
            text=text,
            api_key=self.elevenlabs_api_key,
            voice_id=voice,
            model=self.elevenlabs_model,
            stability=self.voice_stability,
            similarity_boost=self.voice_similarity_boost,
            style=self.voice_style,
            use_speaker_boost=self.use_speaker_boost,
        )

    def _get_provider_order(self) -> list[TtsProvider]:
        """
        Get provider order based on preference.

        Returns:
            List of providers in order to try
        """
        if self.preferred_provider in self.available_providers:
            # Put preferred provider first
            providers = [self.preferred_provider]
            providers.extend([p for p in self.available_providers if p != self.preferred_provider])
            return providers
        else:
            # Default order: ElevenLabs first (better quality), then System
            if TtsProvider.ELEVENLABS in self.available_providers:
                return [TtsProvider.ELEVENLABS, TtsProvider.SYSTEM]
            else:
                return list(self.available_providers)

    def get_available_providers(self) -> list[TtsProvider]:
        """Get list of available TTS providers."""
        return list(self.available_providers)

    def set_character_voice(
        self,
        voice_id: str,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float | None = None,
        use_speaker_boost: bool = True,
    ) -> None:
        """
        Set character-specific voice settings.

        Args:
            voice_id: ElevenLabs voice ID for character
            stability: Voice stability
            similarity_boost: Voice similarity boost
            style: Voice style exaggeration
            use_speaker_boost: Enable speaker boost
        """
        self.default_voice_id = voice_id
        self.voice_stability = stability
        self.voice_similarity_boost = similarity_boost
        self.voice_style = style
        self.use_speaker_boost = use_speaker_boost
