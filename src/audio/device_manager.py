"""Audio device enumeration and management."""

from typing import List, Optional, Tuple

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


def list_audio_devices() -> List[Tuple[int, str, str]]:
    """
    List available audio input and output devices.

    Returns:
        List of tuples: (device_id, device_name, device_type)
        device_type is either 'input', 'output', or 'both'
    """
    if not SOUNDDEVICE_AVAILABLE:
        print("Warning: sounddevice not available, cannot enumerate audio devices")
        return []

    devices = []
    try:
        device_list = sd.query_devices()
        for idx, device in enumerate(device_list):
            device_name = device["name"]
            max_input_channels = device["max_input_channels"]
            max_output_channels = device["max_output_channels"]

            if max_input_channels > 0 and max_output_channels > 0:
                device_type = "both"
            elif max_input_channels > 0:
                device_type = "input"
            elif max_output_channels > 0:
                device_type = "output"
            else:
                continue  # Skip devices with no channels

            devices.append((idx, device_name, device_type))
    except Exception as e:
        print(f"Error enumerating audio devices: {e}")

    return devices


def get_default_input_device() -> Optional[Tuple[int, str]]:
    """
    Get the default audio input device.

    Returns:
        Tuple of (device_id, device_name) or None if not available
    """
    if not SOUNDDEVICE_AVAILABLE:
        return None

    try:
        default_device = sd.query_devices(kind="input")
        device_id = sd.default.device[0]
        device_name = default_device["name"]
        return (device_id, device_name)
    except Exception as e:
        print(f"Error getting default input device: {e}")
        return None


def get_default_output_device() -> Optional[Tuple[int, str]]:
    """
    Get the default audio output device.

    Returns:
        Tuple of (device_id, device_name) or None if not available
    """
    if not SOUNDDEVICE_AVAILABLE:
        return None

    try:
        default_device = sd.query_devices(kind="output")
        device_id = sd.default.device[1]
        device_name = default_device["name"]
        return (device_id, device_name)
    except Exception as e:
        print(f"Error getting default output device: {e}")
        return None


def print_audio_devices() -> None:
    """Print all available audio devices to console (for debugging/CLI)."""
    devices = list_audio_devices()

    if not devices:
        print("No audio devices found")
        return

    print("\nAvailable Audio Devices:")
    print("-" * 60)
    for device_id, device_name, device_type in devices:
        print(f"[{device_id}] {device_name} ({device_type})")
    print("-" * 60)

    default_input = get_default_input_device()
    if default_input:
        print(f"Default input device: [{default_input[0]}] {default_input[1]}")

    default_output = get_default_output_device()
    if default_output:
        print(f"Default output device: [{default_output[0]}] {default_output[1]}")
