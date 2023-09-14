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
import json
import platformdirs
from winutils.fn_lock import core as fn_core
from winutils.toggle_rainmeter import core as rain_core
from winutils.toggle_click import core as click_core
from winutils._helpers import path
from PIL import Image

ICON_PATH = path.ICON_DIR / "settings.ico"
CLICK_HOTKEY = "ctrl+alt+shift+c"
RAIN_HOTKEY = "ctrl+alt+shift+r"
CONFIG_PATH = platformdirs.user_config_path("Winutils", appauthor=False)
SETTINGS_PATH = CONFIG_PATH / "settings.json"


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


class Hooks:
    """Store keyboard hooks used by this tool."""

    fn_hook = None
    click_hotkey = None
    rain_hotkey = None


def change_key_supression(unhook_previous: bool = True) -> None:
    """
    Switch between using suppressive and non-suppressive keyboard hooks.

    When using non-suppressive keyboard hooks, fn lock is disabled completely.

    unhook_previous should be set to False when invoking this function for
    the first time, as it won't attempt to remove previous listeners.
    """
    settings["suppressive_key_events"] = not settings["suppressive_key_events"]

    if unhook_previous:
        if Hooks.fn_hook:
            keyboard.unhook(Hooks.fn_hook)
            Hooks.fn_hook = None
        keyboard.remove_hotkey(Hooks.click_hotkey)
        Hooks.click_hotkey = None
        keyboard.remove_hotkey(Hooks.rain_hotkey)
        Hooks.rain_hotkey = None
    if settings["suppressive_key_events"]:
        Hooks.click_hotkey = keyboard.add_hotkey(CLICK_HOTKEY, invoke_click)
        Hooks.rain_hotkey = keyboard.add_hotkey(RAIN_HOTKEY, invoke_rainmeter)
    else:
        Hooks.fn_hook = keyboard.hook(fn_core.handle_events, suppress=True)
        Hooks.click_hotkey = keyboard.add_hotkey(CLICK_HOTKEY, invoke_click, suppress=True)
        Hooks.rain_hotkey = keyboard.add_hotkey(RAIN_HOTKEY, invoke_rainmeter, suppress=True)

    SETTINGS_PATH.write_text(json.dumps(settings))


CONFIG_PATH.mkdir(parents=True, exist_ok=True)
SETTINGS_PATH.touch(exist_ok=True)
original_toggle_enabled = fn_core.toggle_enabled
fn_core.toggle_enabled = toggle_enabled

settings_string = SETTINGS_PATH.read_text()
if settings_string:
    settings = json.loads(settings_string)
else:
    settings = {"suppressive_key_events": False}

change_key_supression(unhook_previous=False)

icon = Image.open(ICON_PATH)
icon.size = (64, 64)

click_item = pystray.MenuItem("Swap mouse buttons", invoke_click)
rain_item = pystray.MenuItem("Toggle Rainmeter colours", invoke_rainmeter)
fn_lock_item = pystray.MenuItem(
    "Fn Lock", original_toggle_enabled, checked=lambda item: fn_core.State.enabled
)
suppress_item = pystray.MenuItem(
    "Use suppressive events",
    change_key_supression,
    checked=lambda item: settings["suppressive_key_events"],
)
quit_item = pystray.MenuItem("Quit", lambda: tray_icon.stop())

menu = pystray.Menu(
    click_item, rain_item, fn_lock_item, suppress_item, pystray.Menu.SEPARATOR, quit_item
)
tray_icon = pystray.Icon("Winutils", icon=icon, menu=menu)
tray_icon.run()
