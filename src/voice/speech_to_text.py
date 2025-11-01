"""Speech-to-text transcription with multiple provider support."""

import io
import time
from enum import Enum

import numpy as np

try:
    import speech_recognition as sr

    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SttProvider(Enum):
    """Available speech-to-text providers."""

    WEB_SPEECH_API = "web_speech_api"  # Google Web Speech API (free)
    WHISPER_API = "whisper_api"  # OpenAI Whisper API (paid)


class SttError(Exception):
    """Base exception for speech-to-text errors."""

    pass


class SttTimeoutError(SttError):
    """Transcription timeout error."""

    pass


class SttNetworkError(SttError):
    """Network error during transcription."""

    pass


class SttUnclearAudioError(SttError):
    """Audio is unclear or unintelligible."""

    pass


def transcribe_with_web_speech_api(
    audio_data: np.ndarray, sample_rate: int, language: str = "pl-PL"
) -> str:
    """
    Transcribe audio using Google Web Speech API (free).

    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Audio sample rate in Hz
        language: Language code (e.g., "pl-PL", "en-US")

    Returns:
        Transcribed text

    Raises:
        SttError: If transcription fails
        SttTimeoutError: If request times out
        SttNetworkError: If network error occurs
        SttUnclearAudioError: If audio is unintelligible
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        raise SttError("SpeechRecognition library not available")

    recognizer = sr.Recognizer()

    # Convert numpy array to AudioData
    # speech_recognition expects 16-bit PCM data
    audio_int16 = (audio_data * 32767).astype(np.int16)
    audio_bytes = audio_int16.tobytes()

    audio = sr.AudioData(audio_bytes, sample_rate, 2)  # 2 bytes per sample (16-bit)

    try:
        # Use Google Web Speech API
        text = recognizer.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        raise SttUnclearAudioError("Could not understand audio")
    except sr.RequestError as e:
        if "timeout" in str(e).lower():
            raise SttTimeoutError(f"Web Speech API request timed out: {e}")
        else:
            raise SttNetworkError(f"Web Speech API network error: {e}")
    except Exception as e:
        raise SttError(f"Web Speech API error: {e}")


def transcribe_with_whisper_api(
    audio_data: np.ndarray, sample_rate: int, api_key: str, model: str = "whisper-1"
) -> str:
    """
    Transcribe audio using OpenAI Whisper API (paid).

    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Audio sample rate in Hz
        api_key: OpenAI API key
        model: Whisper model to use (default "whisper-1")

    Returns:
        Transcribed text

    Raises:
        SttError: If transcription fails
        SttTimeoutError: If request times out
        SttNetworkError: If network error occurs
    """
    if not OPENAI_AVAILABLE:
        raise SttError("OpenAI library not available")

    if not api_key:
        raise SttError("OpenAI API key not provided")

    try:
        client = OpenAI(api_key=api_key)

        # Convert numpy array to WAV format in memory
        import wave

        # Convert to 16-bit PCM
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes (16-bit)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        wav_buffer.seek(0)

        # Transcribe with Whisper API
        # Create a file-like object with a name attribute (required by OpenAI API)
        wav_buffer.name = "audio.wav"

        response = client.audio.transcriptions.create(model=model, file=wav_buffer)

        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "timed out" in error_msg:
            raise SttTimeoutError(f"Whisper API request timed out: {e}")
        elif "network" in error_msg or "connection" in error_msg:
            raise SttNetworkError(f"Whisper API network error: {e}")
        else:
            raise SttError(f"Whisper API error: {e}")


class SpeechToText:
    """
    Speech-to-text transcription with automatic provider fallback.

    Implements the following fallback chain:
    1. Web Speech API (Google) - Free, fast, good quality
    2. Whisper API (OpenAI) - Paid, high quality, slower
    """

    def __init__(
        self,
        openai_api_key: str = "",
        whisper_model: str = "whisper-1",
        language: str = "pl-PL",
        max_wait_seconds: int = 3,
    ) -> None:
        """
        Initialize speech-to-text transcriber.

        Args:
            openai_api_key: OpenAI API key for Whisper (optional)
            whisper_model: Whisper model to use
            language: Language code for transcription
            max_wait_seconds: Maximum time to wait for transcription
        """
        self.openai_api_key = openai_api_key
        self.whisper_model = whisper_model
        self.language = language
        self.max_wait_seconds = max_wait_seconds

        # Determine available providers
        self.available_providers: list[SttProvider] = []
        if SPEECH_RECOGNITION_AVAILABLE:
            self.available_providers.append(SttProvider.WEB_SPEECH_API)
        if OPENAI_AVAILABLE and openai_api_key:
            self.available_providers.append(SttProvider.WHISPER_API)

    def transcribe(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        preferred_provider: SttProvider | None = None,
    ) -> tuple[str, SttProvider, float]:
        """
        Transcribe audio to text using available providers with automatic fallback.

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Audio sample rate in Hz
            preferred_provider: Preferred provider to try first (optional)

        Returns:
            Tuple of (transcribed_text, provider_used, duration_ms)

        Raises:
            SttError: If all providers fail
        """
        if not self.available_providers:
            raise SttError(
                "No STT providers available. Install SpeechRecognition or provide OpenAI API key."
            )

        # Determine provider order
        providers = self._get_provider_order(preferred_provider)

        last_error: Exception | None = None
        start_time = time.time()

        for provider in providers:
            try:
                if provider == SttProvider.WEB_SPEECH_API:
                    text = transcribe_with_web_speech_api(audio_data, sample_rate, self.language)
                    duration_ms = (time.time() - start_time) * 1000
                    return (text, provider, duration_ms)
                elif provider == SttProvider.WHISPER_API:
                    text = transcribe_with_whisper_api(
                        audio_data, sample_rate, self.openai_api_key, self.whisper_model
                    )
                    duration_ms = (time.time() - start_time) * 1000
                    return (text, provider, duration_ms)
            except SttUnclearAudioError:
                # Don't fallback if audio is unclear - this won't improve with different provider
                raise
            except (SttTimeoutError, SttNetworkError, SttError) as e:
                last_error = e
                print(f"⚠️  {provider.value} failed: {e}, trying next provider...")
                continue

        # All providers failed
        duration_ms = (time.time() - start_time) * 1000
        raise SttError(
            f"All STT providers failed. Last error: {last_error}. Duration: {duration_ms:.0f}ms"
        )

    def _get_provider_order(self, preferred_provider: SttProvider | None) -> list[SttProvider]:
        """
        Get provider order based on preference.

        Args:
            preferred_provider: Preferred provider to try first

        Returns:
            List of providers in order to try
        """
        if preferred_provider and preferred_provider in self.available_providers:
            # Put preferred provider first
            providers = [preferred_provider]
            providers.extend([p for p in self.available_providers if p != preferred_provider])
            return providers
        else:
            # Default order: Web Speech API first (free, fast), then Whisper
            return list(self.available_providers)

    def get_available_providers(self) -> list[SttProvider]:
        """Get list of available STT providers."""
        return list(self.available_providers)
