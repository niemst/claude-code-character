"""Command-line interface for voice-enabled character interaction."""

import argparse
import sys
from pathlib import Path

from src.audio.device_manager import print_audio_devices
from src.character.profile import load_all_character_profiles
from src.config.persistence import get_config_path, load_config, save_config
from src.config.voice_config import create_default_config
from src.hooks.input_hook import send_voice_command
from src.voice.interaction_manager import create_voice_interaction_manager


def cmd_start(args: argparse.Namespace) -> int:
    """
    Start voice interaction.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    print("🎙️  Claude Code Voice Character Interaction\n")

    # Create voice interaction manager
    manager = create_voice_interaction_manager(on_command=send_voice_command)

    # Start voice interaction
    manager.start()

    # Keep running until interrupted
    try:
        print("Press Ctrl+C to stop\n")
        while True:
            import time

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        manager.stop()
        return 0


def cmd_config_show(args: argparse.Namespace) -> int:
    """
    Show current configuration.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config_path = get_config_path()
    print(f"Configuration file: {config_path}\n")

    config = load_config()

    print("Current configuration:")
    print(f"  Voice input enabled: {config.voice_input_enabled}")
    print(f"  Voice output enabled: {config.voice_output_enabled}")
    print(f"  Push-to-talk key: {config.push_to_talk_key}")
    print(f"  Selected character: {config.selected_character or '(none)'}")
    print(f"\nAudio devices:")
    print(f"  Input: {config.audio_devices.input_device or '(default)'}")
    print(f"  Output: {config.audio_devices.output_device or '(default)'}")
    print(f"\nAPI keys:")
    print(f"  OpenAI: {'✓ Set' if config.api_keys.openai else '✗ Not set'}")
    print(f"  ElevenLabs: {'✓ Set' if config.api_keys.elevenlabs else '✗ Not set'}")
    print(f"\nTTS:")
    print(f"  Provider: {config.tts_config.provider}")
    print(f"  ElevenLabs model: {config.tts_config.elevenlabs_model or '(none)'}")
    print(f"\nSTT:")
    print(f"  Whisper model: {config.stt_config.whisper_model}")
    print(f"\nPerformance:")
    print(f"  Max transcription wait: {config.performance.max_transcription_wait_seconds}s")
    print(f"  TTS streaming: {config.performance.tts_streaming_enabled}")

    return 0


def cmd_config_init(args: argparse.Namespace) -> int:
    """
    Initialize default configuration.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config_path = get_config_path()

    if config_path.exists() and not args.force:
        print(f"⚠️  Configuration already exists: {config_path}")
        print("Use --force to overwrite")
        return 1

    config = create_default_config()
    save_config(config)

    print(f"✅ Created default configuration: {config_path}")
    return 0


def cmd_config_enable_voice_input(args: argparse.Namespace) -> int:
    """
    Enable voice input.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = load_config()
    config.voice_input_enabled = True
    save_config(config)
    print("✅ Voice input enabled")
    return 0


def cmd_config_disable_voice_input(args: argparse.Namespace) -> int:
    """
    Disable voice input.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = load_config()
    config.voice_input_enabled = False
    save_config(config)
    print("✅ Voice input disabled")
    return 0


def cmd_config_enable_voice_output(args: argparse.Namespace) -> int:
    """
    Enable voice output.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = load_config()
    config.voice_output_enabled = True
    save_config(config)
    print("✅ Voice output enabled")
    return 0


def cmd_config_disable_voice_output(args: argparse.Namespace) -> int:
    """
    Disable voice output.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = load_config()
    config.voice_output_enabled = False
    save_config(config)
    print("✅ Voice output disabled")
    return 0


def cmd_list_devices(args: argparse.Namespace) -> int:
    """
    List audio devices.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    print_audio_devices()
    return 0


def cmd_list_characters(args: argparse.Namespace) -> int:
    """
    List available characters.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    profiles = load_all_character_profiles()

    if not profiles:
        print("No character profiles found")
        print("\nExpected location: src/character/profiles/*.json")
        return 1

    print("Available characters:\n")
    for name, profile in profiles.items():
        print(f"  {name}:")
        print(f"    Display name: {profile.display_name}")
        print(f"    Description: {profile.description}")
        print(f"    Voice ID: {profile.voice_id}")
        print()

    return 0


def cmd_test_stt(args: argparse.Namespace) -> int:
    """
    Test speech-to-text.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    print("🎤 Testing speech-to-text...")
    print("Press Ctrl+Space and speak, then release to transcribe\n")

    transcription = []

    def on_command(text: str) -> None:
        transcription.append(text)
        print(f"\n✅ Transcription: \"{text}\"\n")

    manager = create_voice_interaction_manager(on_command=on_command)
    manager.start()

    try:
        import time

        time.sleep(30)  # Test for 30 seconds
    except KeyboardInterrupt:
        pass

    manager.stop()

    if transcription:
        print(f"\nTest completed. Transcribed {len(transcription)} command(s)")
        return 0
    else:
        print("\nNo commands transcribed")
        return 1


def cmd_test_tts(args: argparse.Namespace) -> int:
    """
    Test text-to-speech.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    from src.voice.output_manager import create_voice_output_manager

    print("🔊 Testing text-to-speech...\n")

    # Create output manager
    manager = create_voice_output_manager()
    manager.start()

    # Test phrases
    test_phrases = [
        "Hello! This is a test of the text to speech system.",
        "Testing voice output functionality.",
        "If you can hear this, the system is working correctly.",
    ]

    try:
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\nTest {i}/{len(test_phrases)}: \"{phrase}\"")
            manager.speak(phrase)

            # Wait for playback to complete
            import time

            time.sleep(5)

        print("\n✅ TTS test completed")
        return 0

    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        return 1
    finally:
        manager.stop()


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Voice-enabled character interaction for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Start command
    parser_start = subparsers.add_parser("start", help="Start voice interaction")

    # Config commands
    parser_config = subparsers.add_parser("config", help="Configuration commands")
    config_subparsers = parser_config.add_subparsers(dest="config_command")

    parser_config_show = config_subparsers.add_parser("show", help="Show current configuration")
    parser_config_init = config_subparsers.add_parser("init", help="Initialize default configuration")
    parser_config_init.add_argument("--force", action="store_true", help="Overwrite existing configuration")

    parser_config_enable_input = config_subparsers.add_parser("enable-voice-input", help="Enable voice input")
    parser_config_disable_input = config_subparsers.add_parser("disable-voice-input", help="Disable voice input")
    parser_config_enable_output = config_subparsers.add_parser("enable-voice-output", help="Enable voice output")
    parser_config_disable_output = config_subparsers.add_parser("disable-voice-output", help="Disable voice output")

    # List commands
    parser_devices = subparsers.add_parser("list-devices", help="List audio devices")
    parser_characters = subparsers.add_parser("list-characters", help="List available characters")

    # Test commands
    parser_test_stt = subparsers.add_parser("test-stt", help="Test speech-to-text")
    parser_test_tts = subparsers.add_parser("test-tts", help="Test text-to-speech")

    args = parser.parse_args()

    # Route to command handler
    if args.command == "start":
        return cmd_start(args)
    elif args.command == "config":
        if args.config_command == "show":
            return cmd_config_show(args)
        elif args.config_command == "init":
            return cmd_config_init(args)
        elif args.config_command == "enable-voice-input":
            return cmd_config_enable_voice_input(args)
        elif args.config_command == "disable-voice-input":
            return cmd_config_disable_voice_input(args)
        elif args.config_command == "enable-voice-output":
            return cmd_config_enable_voice_output(args)
        elif args.config_command == "disable-voice-output":
            return cmd_config_disable_voice_output(args)
        else:
            parser_config.print_help()
            return 1
    elif args.command == "list-devices":
        return cmd_list_devices(args)
    elif args.command == "list-characters":
        return cmd_list_characters(args)
    elif args.command == "test-stt":
        return cmd_test_stt(args)
    elif args.command == "test-tts":
        return cmd_test_tts(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
