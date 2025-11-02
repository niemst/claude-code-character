"""Input hook for sending voice commands to Claude Code."""

import logging
import sys

logger = logging.getLogger(__name__)


class ClaudeCodeInputHook:
    """
    Hook for sending voice commands to Claude Code's command processor.

    This hook integrates with Claude Code to send transcribed voice commands
    as if they were typed by the user.
    """

    def __init__(self, debug: bool = False) -> None:
        """
        Initialize Claude Code input hook.

        Args:
            debug: Enable debug output
        """
        self.debug = debug
        self._command_count = 0

    def send_command(self, command_text: str) -> None:
        """
        Send a voice command to Claude Code.

        Args:
            command_text: The transcribed command text to send
        """
        if not command_text or not command_text.strip():
            if self.debug:
                logger.debug("Empty command, skipping")
            return

        self._command_count += 1

        # Format command for Claude Code
        formatted_command = command_text.strip()

        if self.debug:
            logger.debug(
                'Sending command #%d to Claude Code: "%s"', self._command_count, formatted_command
            )

        # Send to Claude Code via stdout in a special format
        # Claude Code can detect this pattern and process it as user input
        self._send_to_claude_code(formatted_command)

    def _send_to_claude_code(self, command: str) -> None:
        """
        Send command to Claude Code's input processor.

        This uses a special format that Claude Code can detect and process.

        Args:
            command: Command text to send
        """
        # Option 1: Write to stdout in a special format
        # Claude Code can detect lines with this prefix and treat them as user input
        print(f"[CLAUDE_CODE_VOICE_COMMAND] {command}")
        sys.stdout.flush()

        # Option 2: Write to a named pipe or socket (more robust)
        # TODO: Implement when Claude Code adds official hook support

        # Option 3: Use clipboard (fallback)
        # TODO: Implement clipboard fallback if needed

    def get_command_count(self) -> int:
        """Get the number of commands sent."""
        return self._command_count


# Global hook instance (singleton pattern)
_global_hook: ClaudeCodeInputHook | None = None


def get_input_hook(debug: bool = False) -> ClaudeCodeInputHook:
    """
    Get the global input hook instance.

    Args:
        debug: Enable debug output

    Returns:
        Global ClaudeCodeInputHook instance
    """
    global _global_hook
    if _global_hook is None:
        _global_hook = ClaudeCodeInputHook(debug=debug)
    return _global_hook


def send_voice_command(command_text: str) -> None:
    """
    Send a voice command to Claude Code (convenience function).

    Args:
        command_text: The transcribed command text to send
    """
    hook = get_input_hook()
    hook.send_command(command_text)
