import asyncio
import keyboard
from winutils._helpers import toast

ICON_NAME = "function.ico"
TOGGLE_HOTKEY = "ctrl+alt+home"
FN_KEY_MAPPING = {
    "f1": None,
    "f2": "volume down",
    "f3": "volume up",
    "f4": "volume mute",
    "f5": "stop media",
    "f6": "previous track",
    "f7": "play/pause media",
    "f8": "next track",
    "f9": None,
    "f10": None,
    "f11": None,
    "f12": None,
}
active_callbacks = []
enabled = True


def refresh_callbacks():
    """Add or remove callbacks based on the current state."""
    if enabled:
        active_callbacks.clear()
        for fn_key, action in FN_KEY_MAPPING.items():
            if action is None:
                keyboard.block_key(fn_key)
            else:
                active_callbacks.append(keyboard.remap_key(fn_key, action))
    else:
        for callback in active_callbacks:
            keyboard.unremap_hotkey(callback)
        active_callbacks.clear()


def toggle_enabled():
    """Toggle the fn-lock functionality."""
    global enabled
    enabled = not enabled
    refresh_callbacks()
    status = "enabled" if enabled else "disabled"
    asyncio.run(
        toast.show_toast(
            f"Fn-lock toggled. Currently: {status}",
            toast.get_icon(ICON_NAME)
        )
    )


keyboard.add_hotkey(TOGGLE_HOTKEY, toggle_enabled)
refresh_callbacks()
keyboard.wait()
