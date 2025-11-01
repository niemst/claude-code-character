"""Character personality transformation for voice responses."""

import random
import re
from pathlib import Path
from typing import Optional

from src.character.profile import CharacterProfile, load_all_character_profiles
from src.config.persistence import load_config
from src.config.voice_config import VoiceConfiguration


class TechnicalContentProtector:
    """
    Protects technical content from personality transformation.

    Identifies and preserves:
    - Code blocks (```code```, `code`)
    - File paths (/path/to/file, C:\\path\\to\\file)
    - Error messages
    - URLs
    - Variable names, function names
    - Numbers, versions
    """

    # Regex patterns for technical content
    PATTERNS = [
        # Code blocks
        (r"```[\s\S]*?```", "CODE_BLOCK"),
        (r"`[^`]+`", "INLINE_CODE"),
        # File paths
        (r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*", "WINDOWS_PATH"),
        (r"/(?:[^/\s]+/)*[^/\s]+", "UNIX_PATH"),
        # URLs
        (r"https?://[^\s]+", "URL"),
        # Error messages (common patterns)
        (r"Error:?\s+[^\n]+", "ERROR"),
        (r"Exception:?\s+[^\n]+", "EXCEPTION"),
        (r"Warning:?\s+[^\n]+", "WARNING"),
        # File extensions
        (r"\.\w{1,4}\b", "FILE_EXT"),
        # Version numbers
        (r"\d+\.\d+(?:\.\d+)?", "VERSION"),
        # Function/variable names with common patterns
        (r"\b[a-z_][a-z0-9_]*\(\)", "FUNCTION_CALL"),
        (r"\b[A-Z_][A-Z0-9_]+\b", "CONSTANT"),
    ]

    def __init__(self) -> None:
        """Initialize technical content protector."""
        self._protected_segments: dict[str, str] = {}
        self._counter = 0

    def protect(self, text: str) -> str:
        """
        Replace technical content with placeholders.

        Args:
            text: Original text

        Returns:
            Text with technical content replaced by placeholders
        """
        self._protected_segments = {}
        self._counter = 0

        result = text

        # Apply each pattern
        for pattern, label in self.PATTERNS:
            result = re.sub(pattern, self._create_placeholder, result)

        return result

    def restore(self, text: str) -> str:
        """
        Restore technical content from placeholders.

        Args:
            text: Text with placeholders

        Returns:
            Text with technical content restored
        """
        result = text

        # Replace all placeholders with original content
        for placeholder, original in self._protected_segments.items():
            result = result.replace(placeholder, original)

        return result

    def _create_placeholder(self, match: re.Match) -> str:
        """
        Create placeholder for matched technical content.

        Args:
            match: Regex match object

        Returns:
            Placeholder string
        """
        original = match.group(0)
        placeholder = f"__TECH_{self._counter}__"
        self._protected_segments[placeholder] = original
        self._counter += 1
        return placeholder


class CharacterTransformer:
    """
    Transforms response text to match character personality.

    Applies character personality while preserving 100% technical accuracy.
    """

    def __init__(
        self,
        character_profile: Optional[CharacterProfile] = None,
        config: Optional[VoiceConfiguration] = None,
    ) -> None:
        """
        Initialize character transformer.

        Args:
            character_profile: Character profile to use (loads from config if not provided)
            config: Voice configuration (loads from file if not provided)
        """
        # Load configuration
        if config is None:
            config = load_config()
        self.config = config

        # Load character profile
        if character_profile is None:
            if config.selected_character:
                profiles = load_all_character_profiles()
                character_profile = profiles.get(config.selected_character)

        self.character_profile = character_profile
        self._protector = TechnicalContentProtector()

        # Track if character is active
        self._is_active = character_profile is not None

    def transform(self, text: str) -> tuple[str, bool]:
        """
        Transform text with character personality.

        Args:
            text: Original response text

        Returns:
            Tuple of (transformed_text, was_transformed)
        """
        if not self._is_active or not self.character_profile:
            return (text, False)

        # Protect technical content
        protected_text = self._protector.protect(text)

        # Apply character transformation
        transformed_text = self._apply_personality(protected_text)

        # Restore technical content
        final_text = self._protector.restore(transformed_text)

        return (final_text, True)

    def _apply_personality(self, text: str) -> str:
        """
        Apply character personality to protected text.

        Args:
            text: Text with technical content protected

        Returns:
            Text with personality applied
        """
        if not self.character_profile:
            return text

        result = text

        # Add greeting if configured
        if self.character_profile.transformation_rules.add_greeting:
            result = self._add_greeting(result)

        # Inject characteristic phrases if configured
        if self.character_profile.transformation_rules.use_characteristic_phrases:
            result = self._inject_phrases(result)

        return result

    def _add_greeting(self, text: str) -> str:
        """
        Add character greeting to response.

        Args:
            text: Original text

        Returns:
            Text with greeting added
        """
        if not self.character_profile:
            return text

        # Simple greeting based on character
        # For Toudie: cheerful greetings
        greetings = [
            "Oh! ",
            "Hey there! ",
            "Ah, ",
            "",  # Sometimes no greeting
        ]

        # 30% chance to add greeting
        if random.random() < 0.3:
            greeting = random.choice(greetings)
            return greeting + text

        return text

    def _inject_phrases(self, text: str) -> str:
        """
        Inject characteristic phrases into text.

        Args:
            text: Original text

        Returns:
            Text with phrases injected
        """
        if not self.character_profile:
            return text

        # Don't inject phrases in very short responses
        if len(text) < 50:
            return text

        # 40% chance to inject a phrase
        if random.random() < 0.4:
            phrase = random.choice(self.character_profile.characteristic_phrases)

            # Decide where to inject
            injection_point = random.choice(["start", "end"])

            if injection_point == "start":
                return f"{phrase} {text}"
            else:
                # Add at end, before final punctuation if present
                if text[-1] in ".!?":
                    return f"{text[:-1]}. {phrase}{text[-1]}"
                else:
                    return f"{text} {phrase}"

        return text

    def set_character(self, character_name: Optional[str]) -> None:
        """
        Switch to a different character.

        Args:
            character_name: Name of character to switch to (None to disable)
        """
        if character_name is None:
            self.character_profile = None
            self._is_active = False
            return

        # Load character profile
        profiles = load_all_character_profiles()
        character_profile = profiles.get(character_name)

        if character_profile:
            self.character_profile = character_profile
            self._is_active = True
        else:
            print(f"⚠️  Character '{character_name}' not found")

    def get_voice_settings(self) -> Optional[tuple[str, dict]]:
        """
        Get voice ID and settings for current character.

        Returns:
            Tuple of (voice_id, voice_settings_dict) or None
        """
        if not self.character_profile:
            return None

        voice_settings = {
            "stability": self.character_profile.voice_settings.stability,
            "similarity_boost": self.character_profile.voice_settings.similarity_boost,
            "style": self.character_profile.voice_settings.style,
            "use_speaker_boost": self.character_profile.voice_settings.use_speaker_boost,
        }

        return (self.character_profile.voice_id, voice_settings)

    @property
    def is_active(self) -> bool:
        """Check if character transformation is active."""
        return self._is_active

    @property
    def character_name(self) -> Optional[str]:
        """Get current character name."""
        if self.character_profile:
            return self.character_profile.name
        return None


# Global transformer instance (singleton pattern)
_global_transformer: Optional[CharacterTransformer] = None


def get_character_transformer() -> CharacterTransformer:
    """
    Get the global character transformer instance.

    Returns:
        Global CharacterTransformer instance
    """
    global _global_transformer
    if _global_transformer is None:
        _global_transformer = CharacterTransformer()
    return _global_transformer


def transform_response(text: str) -> tuple[str, bool]:
    """
    Transform response text with character personality (convenience function).

    Args:
        text: Original response text

    Returns:
        Tuple of (transformed_text, was_transformed)
    """
    transformer = get_character_transformer()
    return transformer.transform(text)
