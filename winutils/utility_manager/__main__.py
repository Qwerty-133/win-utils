import sys

if getattr(sys, "frozen", True):
    import psutil
    import os

    current_pid = os.getpid()

    for process in psutil.process_iter(["exe"]):
        if process.info["exe"] == sys.executable and process.pid != current_pid:
            sys.exit(0)


import keyboard
import pystray
from winutils.fn_lock import core as fn_core
from winutils.toggle_rainmeter import core as rain_core
from winutils.toggle_click import core as click_core
from winutils._helpers import path
from PIL import Image

ICON_PATH = path.ICON_DIR / "settings.ico"
CLICK_HOTKEY = "ctrl+alt+shift+c"
RAIN_HOTKEY = "ctrl+alt+shift+r"


def invoke_click() -> None:
    """Run the click tool."""
    new_state = click_core.swap_mouse_buttons()
    click_core.notify_state(new_state)


def invoke_rainmeter() -> None:
    """Run the Rainmeter tool."""
    is_white = rain_core.toggle_colours()
    rain_core.refresh_skins()
    rain_core.notify_state(is_white)


def toggle_enabled() -> None:
    """Invoke the original toggle_enabled function, and update the menu item."""
    original_toggle_enabled()
    tray_icon.update_menu()


original_toggle_enabled = fn_core.toggle_enabled
fn_core.toggle_enabled = toggle_enabled
keyboard.hook(fn_core.handle_events, suppress=True)
keyboard.add_hotkey(CLICK_HOTKEY, invoke_click, suppress=True)
keyboard.add_hotkey(RAIN_HOTKEY, invoke_rainmeter, suppress=True)

icon = Image.open(ICON_PATH)
icon.size = (64, 64)

click_item = pystray.MenuItem(
    "Swap mouse buttons",
    lambda icon, item: invoke_click(),
)
rain_item = pystray.MenuItem(
    "Toggle Rainmeter colours",
    lambda icon, item: invoke_rainmeter(),
)
fn_lock_item = pystray.MenuItem(
    "Fn Lock",
    original_toggle_enabled,
    checked=lambda item: fn_core.State.enabled,
)
quit_item = pystray.MenuItem(
    "Quit",
    lambda: tray_icon.stop(),
)

menu = pystray.Menu(
    click_item,
    rain_item,
    fn_lock_item,
    pystray.Menu.SEPARATOR,
    quit_item,
)
tray_icon = pystray.Icon(
    "Winutils",
    icon=icon,
    menu=menu,
)
tray_icon.run()
