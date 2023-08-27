import asyncio
import win32api
import win32con
import ctypes
from winutils._helpers import toast

ICON_NAME = "cursor.ico"

current_state = win32api.GetSystemMetrics(win32con.SM_SWAPBUTTON)
new_state = 1 - current_state
ctypes.windll.user32.SwapMouseButton(new_state)
new_state_repr = "left" if new_state == 0 else "right"

asyncio.run(
    toast.show_toast(
        "Mouse buttons swapped",
        f"The primary mouse button is now the {new_state_repr} button.",
        toast.get_icon(ICON_NAME)
    )
)
