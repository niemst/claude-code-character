"""Audio capture with push-to-talk hotkey support."""

import threading
from typing import Callable, Optional

import numpy as np
from pynput import keyboard

try:
    import sounddevice as sd

    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class AudioCapture:
    """Manages audio capture with push-to-talk hotkey."""

    def __init__(
        self,
        on_recording_start: Optional[Callable[[], None]] = None,
        on_recording_stop: Optional[Callable[[np.ndarray, int], None]] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        device: Optional[int] = None,
    ) -> None:
        """
        Initialize audio capture.

        Args:
            on_recording_start: Callback when recording starts
            on_recording_stop: Callback when recording stops (receives audio data and sample rate)
            sample_rate: Audio sample rate in Hz (default 16kHz for speech)
            channels: Number of audio channels (default 1 for mono)
            device: Audio input device ID (None for default)
        """
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError("sounddevice is not available - cannot capture audio")

        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

        self._is_recording = False
        self._audio_buffer: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

    def start_recording(self) -> None:
        """Start audio capture."""
        with self._lock:
            if self._is_recording:
                return  # Already recording

            self._audio_buffer = []
            self._is_recording = True

            # Create and start audio input stream
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device,
                callback=self._audio_callback,
            )
            self._stream.start()

            if self.on_recording_start:
                self.on_recording_start()

    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop audio capture and return recorded audio.

        Returns:
            Numpy array of audio samples, or None if no audio recorded
        """
        with self._lock:
            if not self._is_recording:
                return None

            self._is_recording = False

            # Stop and close stream
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            # Concatenate all audio chunks
            if not self._audio_buffer:
                return None

            audio_data = np.concatenate(self._audio_buffer, axis=0)

            # Call callback with recorded audio
            if self.on_recording_stop:
                self.on_recording_stop(audio_data, self.sample_rate)

            return audio_data

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info: object, status: sd.CallbackFlags
    ) -> None:
        """
        Callback for audio input stream.

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Stream status flags
        """
        if status:
            print(f"Audio capture status: {status}")

        if self._is_recording:
            # Copy audio data to buffer
            self._audio_buffer.append(indata.copy())

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording


class PushToTalkListener:
    """Global hotkey listener for push-to-talk."""

    def __init__(
        self,
        hotkey: str = "ctrl+space",
        on_press: Optional[Callable[[], None]] = None,
        on_release: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize push-to-talk listener.

        Args:
            hotkey: Hotkey combination (e.g., "ctrl+space", "alt+space")
            on_press: Callback when hotkey is pressed
            on_release: Callback when hotkey is released
        """
        self.hotkey = hotkey
        self.on_press = on_press
        self.on_release = on_release

        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._is_active = False
        self._hotkey_pressed = False

    def start(self) -> None:
        """Start listening for hotkey."""
        if self._is_active:
            return

        # Parse hotkey string into pynput format
        # Convert "ctrl+space" to "<ctrl>+<space>"
        hotkey_pynput = self._parse_hotkey(self.hotkey)

        # Create hotkey mappings
        hotkey_map = {
            hotkey_pynput: self._on_hotkey_press,
        }

        # Create and start global hotkey listener
        self._listener = keyboard.GlobalHotKeys(hotkey_map)
        self._listener.start()
        self._is_active = True

        print(f"Push-to-talk listener started (hotkey: {self.hotkey})")

    def stop(self) -> None:
        """Stop listening for hotkey."""
        if not self._is_active:
            return

        if self._listener:
            self._listener.stop()
            self._listener = None

        self._is_active = False
        print("Push-to-talk listener stopped")

    def _parse_hotkey(self, hotkey: str) -> str:
        """
        Parse hotkey string to pynput format.

        Args:
            hotkey: Hotkey in format "ctrl+space", "alt+shift+a", etc.

        Returns:
            Hotkey in pynput format "<ctrl>+<space>"
        """
        parts = hotkey.lower().split("+")
        pynput_parts = []

        for part in parts:
            part = part.strip()
            # Special keys need angle brackets
            if part in ["ctrl", "alt", "shift", "cmd", "win"]:
                pynput_parts.append(f"<{part}>")
            else:
                # Regular keys
                pynput_parts.append(part)

        return "+".join(pynput_parts)

    def _on_hotkey_press(self) -> None:
        """Handle hotkey press (called by pynput)."""
        if not self._hotkey_pressed:
            self._hotkey_pressed = True
            if self.on_press:
                self.on_press()

        # Note: We need a separate key listener to detect release
        # GlobalHotKeys only detects the full combination press
        # For now, we'll use a timed approach or separate listener

    def _on_hotkey_release(self) -> None:
        """Handle hotkey release."""
        if self._hotkey_pressed:
            self._hotkey_pressed = False
            if self.on_release:
                self.on_release()

    @property
    def is_active(self) -> bool:
        """Check if listener is active."""
        return self._is_active


class PushToTalkHandler:
    """
    Complete push-to-talk handler combining hotkey listener and audio capture.

    This class manages the full push-to-talk workflow:
    1. User presses hotkey -> start recording
    2. User releases hotkey -> stop recording and process audio
    """

    def __init__(
        self,
        hotkey: str = "ctrl+space",
        on_audio_captured: Optional[Callable[[np.ndarray, int], None]] = None,
        sample_rate: int = 16000,
        device: Optional[int] = None,
    ) -> None:
        """
        Initialize push-to-talk handler.

        Args:
            hotkey: Hotkey combination for push-to-talk
            on_audio_captured: Callback when audio is captured (receives audio data and sample rate)
            sample_rate: Audio sample rate
            device: Audio input device ID
        """
        self.hotkey = hotkey
        self.on_audio_captured = on_audio_captured

        # Create audio capture
        self.audio_capture = AudioCapture(
            on_recording_start=self._on_recording_start,
            on_recording_stop=self._on_recording_stop,
            sample_rate=sample_rate,
            device=device,
        )

        # Create hotkey listener
        # Note: pynput's GlobalHotKeys has limitations with detecting key release
        # We'll use a regular keyboard listener instead for better control
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._ctrl_pressed = False
        self._space_pressed = False
        self._is_active = False

    def start(self) -> None:
        """Start push-to-talk handler."""
        if self._is_active:
            return

        # Start keyboard listener
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release
        )
        self._keyboard_listener.start()
        self._is_active = True

        print(f"Push-to-talk handler started (hotkey: {self.hotkey})")

    def stop(self) -> None:
        """Stop push-to-talk handler."""
        if not self._is_active:
            return

        # Stop keyboard listener
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        # Stop recording if active
        if self.audio_capture.is_recording:
            self.audio_capture.stop_recording()

        self._is_active = False
        print("Push-to-talk handler stopped")

    def _on_key_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Handle key press events."""
        # Track modifier keys
        if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self._ctrl_pressed = True
        elif hasattr(key, "char") and key.char == " ":
            self._space_pressed = True
        elif key == keyboard.Key.space:
            self._space_pressed = True

        # Check if hotkey combination is pressed
        if self._ctrl_pressed and self._space_pressed:
            if not self.audio_capture.is_recording:
                self.audio_capture.start_recording()

    def _on_key_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Handle key release events."""
        # Track modifier keys
        if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self._ctrl_pressed = False
        elif hasattr(key, "char") and key.char == " ":
            self._space_pressed = False
        elif key == keyboard.Key.space:
            self._space_pressed = False

        # Check if hotkey combination is released
        if not (self._ctrl_pressed and self._space_pressed):
            if self.audio_capture.is_recording:
                self.audio_capture.stop_recording()

    def _on_recording_start(self) -> None:
        """Callback when recording starts."""
        print("🎤 Recording started...")

    def _on_recording_stop(self, audio_data: np.ndarray, sample_rate: int) -> None:
        """
        Callback when recording stops.

        Args:
            audio_data: Recorded audio samples
            sample_rate: Audio sample rate
        """
        print("🎤 Recording stopped")

        # Call user callback
        if self.on_audio_captured:
            self.on_audio_captured(audio_data, sample_rate)

    @property
    def is_active(self) -> bool:
        """Check if handler is active."""
        return self._is_active
