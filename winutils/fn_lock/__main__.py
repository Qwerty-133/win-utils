import keyboard
from winutils._helpers import toast

ICON_NAME = "function.ico"
FN_KEY_MAPPING = {
    "f1": "select media",
    "f2": "volume down",
    "f3": "volume up",
    "f4": "volume mute",
    "f5": "stop media",
    "f6": "previous track",
    "f7": "play/pause media",
    "f8": "next track",
    "f9": "start mail",
    "f10": "browser start and home",
    "f11": "start application 1",
    "f12": "start application 2",
}


class State:
    """Holds application global state."""

    enabled = True
    insert_held = False
    ctrl_held = False
    alt_held = False


def toggle_enabled():
    """Toggle the enabled state."""
    State.enabled = not State.enabled
    status = "enabled" if State.enabled else "disabled"
    toast.show_toast(
        "Fn-lock toggled.",
        f"Fn-lock is currently {status}.",
        toast.get_icon(ICON_NAME),
        "Fn Lock",
    )


def handle(e):
    """
    Handle the fn-lock functionality.

    If fn-lock is enabled, the function keys will be remapped to their
    media key counterparts, unless the insert key is held.

    ctrl+alt+insert will toggle the enabled state.
    """
    pressed = e.event_type == keyboard.KEY_DOWN

    if e.name == "insert":
        State.insert_held = pressed
        if State.alt_held and State.ctrl_held and State.insert_held:
            toggle_enabled()
        return False
    if e.name == "ctrl":
        State.ctrl_held = pressed
    elif e.name == "alt":
        State.alt_held = pressed

    if State.enabled and e.name in FN_KEY_MAPPING and not State.insert_held:
        target = FN_KEY_MAPPING[e.name]
    else:
        return True

    if pressed:
        keyboard.press(target)
    elif e.event_type == keyboard.KEY_UP:
        keyboard.release(target)
    return False


keyboard.hook(handle, suppress=True)
keyboard.wait()
