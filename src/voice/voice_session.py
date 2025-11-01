"""Voice session state management during runtime."""

import uuid
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class PendingResponse:
    """A response waiting to be spoken."""

    text: str
    timestamp: int
    character_transformed: bool


@dataclass
class LastCommand:
    """Information about the last voice command."""

    spoken_text: str
    transcribed_text: str
    timestamp: int
    transcription_duration_ms: int


@dataclass
class Statistics:
    """Performance statistics for the voice session."""

    commands_issued_count: int = 0
    average_transcription_time_ms: float = 0.0
    average_playback_start_time_ms: float = 0.0
    interruptions_count: int = 0

    def update_transcription_time(self, duration_ms: int) -> None:
        """Update average transcription time with new measurement."""
        total = self.average_transcription_time_ms * self.commands_issued_count
        self.commands_issued_count += 1
        self.average_transcription_time_ms = (total + duration_ms) / self.commands_issued_count

    def update_playback_start_time(self, duration_ms: int) -> None:
        """Update average playback start time with new measurement."""
        count = max(1, self.commands_issued_count)
        total = self.average_playback_start_time_ms * (count - 1)
        self.average_playback_start_time_ms = (total + duration_ms) / count

    def increment_interruptions(self) -> None:
        """Increment interruption counter."""
        self.interruptions_count += 1


@dataclass
class VoiceSession:
    """Active voice interaction state during runtime (in-memory only)."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_listening: bool = False
    is_playing: bool = False
    current_audio_stream: Optional[Any] = None
    pending_responses: List[PendingResponse] = field(default_factory=list)
    last_command: Optional[LastCommand] = None
    statistics: Statistics = field(default_factory=Statistics)

    def __post_init__(self) -> None:
        """Validate mutual exclusion constraint."""
        if self.is_listening and self.is_playing:
            raise ValueError("is_listening and is_playing cannot both be True")

    def set_listening(self, listening: bool) -> None:
        """Set listening state with mutual exclusion enforcement."""
        if listening and self.is_playing:
            raise ValueError("Cannot start listening while playing")
        self.is_listening = listening

    def set_playing(self, playing: bool) -> None:
        """Set playing state with mutual exclusion enforcement."""
        if playing and self.is_listening:
            raise ValueError("Cannot start playing while listening")
        self.is_playing = playing

    def queue_response(self, text: str, timestamp: int, character_transformed: bool) -> None:
        """Add a response to the pending queue."""
        self.pending_responses.append(
            PendingResponse(
                text=text, timestamp=timestamp, character_transformed=character_transformed
            )
        )

    def dequeue_response(self) -> Optional[PendingResponse]:
        """Remove and return the next response from the queue (FIFO)."""
        if self.pending_responses:
            return self.pending_responses.pop(0)
        return None
