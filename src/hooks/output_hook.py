"""Output hook for intercepting Claude Code responses and converting to speech."""

from collections.abc import Callable


class ClaudeCodeOutputHook:
    """
    Hook for intercepting Claude Code's text responses and converting them to speech.

    This hook monitors Claude Code's output and queues responses for TTS playback.
    """

    def __init__(
        self,
        on_response: Callable[[str], None] | None = None,
        min_response_length: int = 5,
        debug: bool = False,
    ) -> None:
        """
        Initialize Claude Code output hook.

        Args:
            on_response: Callback when response is intercepted (receives response text)
            min_response_length: Minimum response length to trigger TTS
            debug: Enable debug output
        """
        self.on_response = on_response
        self.min_response_length = min_response_length
        self.debug = debug

        self._response_count = 0
        self._original_stdout = None
        self._is_monitoring = False

    def start_monitoring(self) -> None:
        """
        Start monitoring Claude Code output.

        Note: This is a simplified version. In production, this would integrate
        with Claude Code's actual response mechanism.
        """
        if self._is_monitoring:
            return

        self._is_monitoring = True

        if self.debug:
            print("📡 Output hook monitoring started")

    def stop_monitoring(self) -> None:
        """Stop monitoring Claude Code output."""
        if not self._is_monitoring:
            return

        self._is_monitoring = False

        if self.debug:
            print("📡 Output hook monitoring stopped")

    def intercept_response(self, response_text: str) -> None:
        """
        Manually intercept a Claude Code response.

        This method should be called by the integration layer when
        Claude Code produces a response.

        Args:
            response_text: The response text from Claude Code
        """
        if not self._is_monitoring:
            return

        # Filter out empty or very short responses
        if not response_text or len(response_text.strip()) < self.min_response_length:
            if self.debug:
                print(f"⚠️  Response too short, skipping TTS: {len(response_text)} chars")
            return

        # Filter out command-like responses (optional)
        if response_text.strip().startswith("[CLAUDE_CODE_"):
            if self.debug:
                print("⚠️  Skipping internal command response")
            return

        self._response_count += 1

        if self.debug:
            print(f'📥 Intercepted response #{self._response_count}: "{response_text[:50]}..."')

        # Call response callback
        if self.on_response:
            self.on_response(response_text)

    def get_response_count(self) -> int:
        """Get the number of responses intercepted."""
        return self._response_count

    @property
    def is_monitoring(self) -> bool:
        """Check if currently monitoring output."""
        return self._is_monitoring


# Global hook instance (singleton pattern)
_global_output_hook: ClaudeCodeOutputHook | None = None


def get_output_hook(debug: bool = False) -> ClaudeCodeOutputHook:
    """
    Get the global output hook instance.

    Args:
        debug: Enable debug output

    Returns:
        Global ClaudeCodeOutputHook instance
    """
    global _global_output_hook
    if _global_output_hook is None:
        _global_output_hook = ClaudeCodeOutputHook(debug=debug)
    return _global_output_hook


def intercept_claude_response(response_text: str) -> None:
    """
    Intercept a Claude Code response (convenience function).

    Args:
        response_text: The response text from Claude Code
    """
    hook = get_output_hook()
    hook.intercept_response(response_text)
