"""Audio playback with streaming and interrupt support."""

import io
import threading
import time
import wave
from typing import Callable, Iterator, Optional

import numpy as np

try:
    import sounddevice as sd

    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class PlaybackError(Exception):
    """Base exception for playback errors."""

    pass


class AudioPlayer:
    """
    Audio player with support for WAV, MP3, and raw audio.

    Supports:
    - Regular playback from bytes
    - Streaming playback from generator
    - Interrupt handling
    - Playback state callbacks
    """

    def __init__(
        self,
        on_playback_start: Optional[Callable[[], None]] = None,
        on_playback_stop: Optional[Callable[[], None]] = None,
        device: Optional[int] = None,
    ) -> None:
        """
        Initialize audio player.

        Args:
            on_playback_start: Callback when playback starts
            on_playback_stop: Callback when playback stops
            device: Audio output device ID (None for default)
        """
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError("sounddevice is not available - cannot play audio")

        self.on_playback_start = on_playback_start
        self.on_playback_stop = on_playback_stop
        self.device = device

        self._is_playing = False
        self._should_stop = False
        self._stream: Optional[sd.OutputStream] = None
        self._playback_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def play(self, audio_data: bytes, audio_format: str = "auto") -> None:
        """
        Play audio from bytes.

        Args:
            audio_data: Audio data as bytes
            audio_format: Audio format ('wav', 'mp3', or 'auto' for detection)

        Raises:
            PlaybackError: If playback fails
        """
        if self._is_playing:
            raise PlaybackError("Already playing audio")

        # Detect format if auto
        if audio_format == "auto":
            audio_format = self._detect_format(audio_data)

        # Convert to numpy array based on format
        if audio_format == "wav":
            audio_array, sample_rate = self._load_wav(audio_data)
        elif audio_format == "mp3":
            audio_array, sample_rate = self._load_mp3(audio_data)
        else:
            raise PlaybackError(f"Unsupported audio format: {audio_format}")

        # Play audio
        self._play_array(audio_array, sample_rate)

    def play_streaming(
        self, audio_stream: Iterator[bytes], sample_rate: int = 44100, channels: int = 1
    ) -> None:
        """
        Play audio from streaming chunks.

        Args:
            audio_stream: Iterator yielding audio chunks as bytes
            sample_rate: Sample rate in Hz
            channels: Number of audio channels

        Raises:
            PlaybackError: If playback fails
        """
        if self._is_playing:
            raise PlaybackError("Already playing audio")

        with self._lock:
            self._is_playing = True
            self._should_stop = False

        if self.on_playback_start:
            self.on_playback_start()

        try:
            # Create output stream
            self._stream = sd.OutputStream(
                samplerate=sample_rate, channels=channels, device=self.device
            )
            self._stream.start()

            # Play chunks as they arrive
            for chunk in audio_stream:
                if self._should_stop:
                    break

                # Convert MP3 bytes to audio array (for ElevenLabs)
                # This is simplified - in production, use proper MP3 decoder
                # For now, we'll use pydub or similar
                try:
                    # Try to decode as MP3
                    audio_array = self._decode_mp3_chunk(chunk)
                    self._stream.write(audio_array)
                except Exception as e:
                    print(f"Warning: Failed to decode audio chunk: {e}")
                    continue

        except Exception as e:
            raise PlaybackError(f"Streaming playback error: {e}")
        finally:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            with self._lock:
                self._is_playing = False

            if self.on_playback_stop:
                self.on_playback_stop()

    def stop(self) -> None:
        """Stop current playback."""
        with self._lock:
            if not self._is_playing:
                return

            self._should_stop = True

        # Wait for playback to stop
        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=2.0)

    def _play_array(self, audio_array: np.ndarray, sample_rate: int) -> None:
        """
        Play audio from numpy array.

        Args:
            audio_array: Audio samples as numpy array
            sample_rate: Sample rate in Hz
        """
        with self._lock:
            self._is_playing = True
            self._should_stop = False

        if self.on_playback_start:
            self.on_playback_start()

        try:
            # Play audio using sounddevice
            sd.play(audio_array, sample_rate, device=self.device)
            sd.wait()  # Wait until playback finishes

        except Exception as e:
            raise PlaybackError(f"Playback error: {e}")
        finally:
            with self._lock:
                self._is_playing = False

            if self.on_playback_stop:
                self.on_playback_stop()

    def _detect_format(self, audio_data: bytes) -> str:
        """
        Detect audio format from magic bytes.

        Args:
            audio_data: Audio data bytes

        Returns:
            Format string ('wav' or 'mp3')
        """
        if audio_data.startswith(b"RIFF"):
            return "wav"
        elif audio_data.startswith(b"ID3") or audio_data.startswith(b"\xff\xfb"):
            return "mp3"
        else:
            # Default to WAV
            return "wav"

    def _load_wav(self, wav_data: bytes) -> tuple[np.ndarray, int]:
        """
        Load WAV audio from bytes.

        Args:
            wav_data: WAV file bytes

        Returns:
            Tuple of (audio_array, sample_rate)
        """
        with io.BytesIO(wav_data) as wav_io:
            with wave.open(wav_io, "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                n_frames = wav_file.getnframes()

                # Read all frames
                frames = wav_file.readframes(n_frames)

                # Convert to numpy array
                if sample_width == 1:
                    dtype = np.uint8
                elif sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                else:
                    raise PlaybackError(f"Unsupported sample width: {sample_width}")

                audio_array = np.frombuffer(frames, dtype=dtype)

                # Reshape for multi-channel
                if n_channels > 1:
                    audio_array = audio_array.reshape(-1, n_channels)

                # Normalize to float32 [-1.0, 1.0]
                if dtype == np.uint8:
                    audio_array = (audio_array.astype(np.float32) - 128) / 128.0
                elif dtype == np.int16:
                    audio_array = audio_array.astype(np.float32) / 32768.0
                elif dtype == np.int32:
                    audio_array = audio_array.astype(np.float32) / 2147483648.0

                return (audio_array, sample_rate)

    def _load_mp3(self, mp3_data: bytes) -> tuple[np.ndarray, int]:
        """
        Load MP3 audio from bytes.

        Args:
            mp3_data: MP3 file bytes

        Returns:
            Tuple of (audio_array, sample_rate)
        """
        try:
            from pydub import AudioSegment

            # Load MP3 using pydub
            audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))

            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())

            # Normalize to float32 [-1.0, 1.0]
            if audio.sample_width == 1:
                samples = (samples.astype(np.float32) - 128) / 128.0
            elif audio.sample_width == 2:
                samples = samples.astype(np.float32) / 32768.0
            elif audio.sample_width == 4:
                samples = samples.astype(np.float32) / 2147483648.0

            # Reshape for stereo
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))

            return (samples, audio.frame_rate)

        except ImportError:
            raise PlaybackError(
                "MP3 playback requires pydub. Install with: pip install pydub"
            )
        except Exception as e:
            raise PlaybackError(f"Failed to load MP3: {e}")

    def _decode_mp3_chunk(self, chunk: bytes) -> np.ndarray:
        """
        Decode MP3 chunk to audio array.

        Args:
            chunk: MP3 audio chunk

        Returns:
            Audio array

        Note: This is simplified for MVP. Production should use proper streaming decoder.
        """
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_mp3(io.BytesIO(chunk))
            samples = np.array(audio.get_array_of_samples())

            # Normalize
            if audio.sample_width == 2:
                samples = samples.astype(np.float32) / 32768.0

            if audio.channels == 2:
                samples = samples.reshape((-1, 2))

            return samples

        except Exception:
            # Return silence if decode fails
            return np.zeros((1024, 1), dtype=np.float32)

    @property
    def is_playing(self) -> bool:
        """Check if currently playing audio."""
        return self._is_playing


class PlaybackController:
    """
    Controller for managing playback queue and interrupts.

    Features:
    - FIFO response queue
    - Sequential playback
    - Interrupt handling
    - Performance monitoring
    """

    def __init__(
        self,
        player: AudioPlayer,
        on_queue_empty: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize playback controller.

        Args:
            player: AudioPlayer instance
            on_queue_empty: Callback when queue becomes empty
        """
        self.player = player
        self.on_queue_empty = on_queue_empty

        self._queue: list[tuple[bytes, str, int]] = []  # (audio_data, format, timestamp)
        self._lock = threading.Lock()
        self._controller_thread: Optional[threading.Thread] = None
        self._is_active = False
        self._should_stop = False

    def start(self) -> None:
        """Start playback controller."""
        if self._is_active:
            return

        self._is_active = True
        self._should_stop = False

        # Start controller thread
        self._controller_thread = threading.Thread(target=self._controller_loop, daemon=True)
        self._controller_thread.start()

        print("✅ Playback controller started")

    def stop(self) -> None:
        """Stop playback controller."""
        if not self._is_active:
            return

        self._should_stop = True

        # Stop current playback
        self.player.stop()

        # Wait for controller thread
        if self._controller_thread and self._controller_thread.is_alive():
            self._controller_thread.join(timeout=2.0)

        self._is_active = False
        print("✅ Playback controller stopped")

    def queue_audio(self, audio_data: bytes, audio_format: str = "auto") -> None:
        """
        Add audio to playback queue.

        Args:
            audio_data: Audio data bytes
            audio_format: Audio format ('wav', 'mp3', 'auto')
        """
        timestamp = int(time.time() * 1000)

        with self._lock:
            self._queue.append((audio_data, audio_format, timestamp))

    def interrupt(self) -> int:
        """
        Interrupt current playback.

        Returns:
            Interrupt latency in milliseconds
        """
        start_time = time.time()

        # Stop current playback
        self.player.stop()

        # Clear queue
        with self._lock:
            self._queue.clear()

        interrupt_latency = int((time.time() - start_time) * 1000)
        return interrupt_latency

    def _controller_loop(self) -> None:
        """Main controller loop for processing playback queue."""
        while not self._should_stop:
            # Check if there's audio in queue
            audio_item = None
            with self._lock:
                if self._queue:
                    audio_item = self._queue.pop(0)

            if audio_item:
                audio_data, audio_format, timestamp = audio_item

                try:
                    # Play audio
                    self.player.play(audio_data, audio_format)
                except Exception as e:
                    print(f"❌ Playback error: {e}")

            else:
                # Queue empty
                if self.on_queue_empty:
                    self.on_queue_empty()

                # Sleep briefly
                time.sleep(0.1)

    def get_queue_size(self) -> int:
        """Get current queue size."""
        with self._lock:
            return len(self._queue)

    @property
    def is_active(self) -> bool:
        """Check if controller is active."""
        return self._is_active
