"""Character profile data structures and loading."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VoiceSettings:
    """ElevenLabs voice settings for character."""

    stability: float
    similarity_boost: float
    style: float | None = None
    use_speaker_boost: bool | None = None

    def __post_init__(self) -> None:
        """Validate voice settings ranges."""
        if not 0.0 <= self.stability <= 1.0:
            raise ValueError(f"stability must be 0.0-1.0, got {self.stability}")
        if not 0.0 <= self.similarity_boost <= 1.0:
            raise ValueError(f"similarity_boost must be 0.0-1.0, got {self.similarity_boost}")
        if self.style is not None and not 0.0 <= self.style <= 1.0:
            raise ValueError(f"style must be 0.0-1.0, got {self.style}")


@dataclass
class TransformationRules:
    """Rules for applying character personality to text."""

    add_greeting: bool
    use_characteristic_phrases: bool
    preserve_technical_content: bool

    def __post_init__(self) -> None:
        """Enforce preserve_technical_content must be True."""
        if not self.preserve_technical_content:
            raise ValueError("preserve_technical_content MUST be True")


@dataclass
class CharacterProfile:
    """Character personality and voice configuration."""

    name: str
    display_name: str
    description: str
    voice_id: str
    voice_settings: VoiceSettings
    system_prompt: str
    characteristic_phrases: list[str]
    transformation_rules: TransformationRules

    def __post_init__(self) -> None:
        """Validate character profile."""
        if not self.name.replace("-", "").isalnum():
            raise ValueError(f"name must be alphanumeric with hyphens: {self.name}")
        if not self.display_name:
            raise ValueError("display_name cannot be empty")
        if not self.system_prompt or len(self.system_prompt) > 500:
            raise ValueError("system_prompt must be 1-500 characters")
        if not 3 <= len(self.characteristic_phrases) <= 10:
            count = len(self.characteristic_phrases)
            raise ValueError(f"characteristic_phrases must have 3-10 items, got {count}")


def load_character_profile(profile_path: Path) -> CharacterProfile:
    """Load a character profile from JSON file."""
    with open(profile_path, encoding="utf-8") as f:
        data = json.load(f)

    return CharacterProfile(
        name=data["name"],
        display_name=data["display_name"],
        description=data["description"],
        voice_id=data["voice_id"],
        voice_settings=VoiceSettings(
            stability=data["voice_settings"]["stability"],
            similarity_boost=data["voice_settings"]["similarity_boost"],
            style=data["voice_settings"].get("style"),
            use_speaker_boost=data["voice_settings"].get("use_speaker_boost"),
        ),
        system_prompt=data["system_prompt"],
        characteristic_phrases=data["characteristic_phrases"],
        transformation_rules=TransformationRules(
            add_greeting=data["transformation_rules"]["add_greeting"],
            use_characteristic_phrases=data["transformation_rules"]["use_characteristic_phrases"],
            preserve_technical_content=data["transformation_rules"]["preserve_technical_content"],
        ),
    )


def load_all_character_profiles() -> dict[str, CharacterProfile]:
    """Load all character profiles from src/character/profiles/*.json."""
    profiles_dir = Path(__file__).parent / "profiles"
    profiles: dict[str, CharacterProfile] = {}

    if not profiles_dir.exists():
        return profiles

    for profile_file in profiles_dir.glob("*.json"):
        try:
            profile = load_character_profile(profile_file)
            profiles[profile.name] = profile
        except Exception as e:
            print(f"Warning: Failed to load character profile {profile_file.name}: {e}")

    return profiles
