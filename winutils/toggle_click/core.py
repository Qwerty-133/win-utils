"""The core functionality for toggling the primary mouse button."""
ICON_NAME = "cursor.ico"


def swap_mouse_buttons() -> int:
    """Swap the primary mouse button and return the current primary button."""
    import win32api
    import win32con
    import ctypes

    current_state = win32api.GetSystemMetrics(win32con.SM_SWAPBUTTON)
    new_state = 1 - current_state
    ctypes.windll.user32.SwapMouseButton(new_state)
    return new_state


def notify_state(state: int) -> None:
    """Show a toast for the current primary mouse button state."""
    from winutils._helpers import toast

    state_repr = "left" if state == 0 else "right"
    toast.show_toast(
        "Mouse buttons swapped",
        f"The primary mouse button is now the {state_repr} button.",
        toast.get_icon(ICON_NAME),
        "Toggle Click",
    )
