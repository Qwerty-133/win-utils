import sys

if getattr(sys, "frozen", False):
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
from winutils.mechvibes_volume import core as mech_core
from winutils._helpers import path, overlay
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


def mech_start_hook() -> None:
    settings["mechvibes_enabled"] = True
    SETTINGS_PATH.write_text(json.dumps(settings))

    if settings["suppressive_key_events"]:
        Hooks.increase_mech_hotkey = keyboard.add_hotkey(
            mech_core.INCREASE_HOTKEY, mech_core.Handler.increment_scaling, suppress=True
        )
        Hooks.decrease_mech_hotkey = keyboard.add_hotkey(
            mech_core.DECREASE_HOTKEY, mech_core.Handler.decrement_scaling, suppress=True
        )
    else:
        Hooks.increase_mech_hotkey = keyboard.add_hotkey(
            mech_core.INCREASE_HOTKEY, mech_core.Handler.increment_scaling
        )
        Hooks.decrease_mech_hotkey = keyboard.add_hotkey(
            mech_core.DECREASE_HOTKEY, mech_core.Handler.decrement_scaling
        )


def mech_stop_hook() -> None:
    settings["mechvibes_enabled"] = False
    SETTINGS_PATH.write_text(json.dumps(settings))

    keyboard.remove_hotkey(Hooks.increase_mech_hotkey)
    Hooks.increase_mech_hotkey = None
    keyboard.remove_hotkey(Hooks.decrease_mech_hotkey)
    Hooks.decrease_mech_hotkey = None


class Hooks:
    """Store keyboard hooks used by this tool."""

    fn_hook = None
    click_hotkey = None
    rain_hotkey = None
    increase_mech_hotkey = None
    decrease_mech_hotkey = None


def initialize_hooks() -> None:
    """
    Start all keyboard hooks, keeping in mind the suppression configuration.
    """
    if settings["suppressive_key_events"]:
        Hooks.click_hotkey = keyboard.add_hotkey(CLICK_HOTKEY, invoke_click)
        Hooks.rain_hotkey = keyboard.add_hotkey(RAIN_HOTKEY, invoke_rainmeter)
    else:
        Hooks.fn_hook = keyboard.hook(fn_core.handle_events, suppress=True)
        Hooks.click_hotkey = keyboard.add_hotkey(CLICK_HOTKEY, invoke_click, suppress=True)
        Hooks.rain_hotkey = keyboard.add_hotkey(RAIN_HOTKEY, invoke_rainmeter, suppress=True)


def change_key_supression() -> None:
    """
    Switch between using suppressive and non-suppressive keyboard hooks.

    When using non-suppressive keyboard hooks, fn lock is disabled completely.
    """
    settings["suppressive_key_events"] = not settings["suppressive_key_events"]
    SETTINGS_PATH.write_text(json.dumps(settings))

    if Hooks.fn_hook:
        keyboard.unhook(Hooks.fn_hook)
        Hooks.fn_hook = None
    keyboard.remove_hotkey(Hooks.click_hotkey)
    Hooks.click_hotkey = None
    keyboard.remove_hotkey(Hooks.rain_hotkey)
    Hooks.rain_hotkey = None

    if settings["mechvibes_enabled"]:
        mech_stop_hook()
        mech_start_hook()

    initialize_hooks()


CONFIG_PATH.mkdir(parents=True, exist_ok=True)
SETTINGS_PATH.touch(exist_ok=True)

original_toggle_enabled = fn_core.toggle_enabled
fn_core.toggle_enabled = toggle_enabled

mech_core.Handler.start_hook = mech_start_hook
mech_core.Handler.stop_hook = mech_stop_hook

settings_string = SETTINGS_PATH.read_text()
if settings_string:
    settings = json.loads(settings_string)
else:
    settings = {"suppressive_key_events": False, "mechvibes_enabled": False}
if settings["mechvibes_enabled"]:
    mech_core.Handler.start()

initialize_hooks()

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
mechvibes_item = pystray.MenuItem(
    "Mechvibes Stable Audio",
    mech_core.Handler.toggle,
    checked=lambda item: mech_core.Handler.running,
)
quit_item = pystray.MenuItem("Quit", lambda: tray_icon.stop())

menu = pystray.Menu(
    click_item,
    rain_item,
    fn_lock_item,
    mechvibes_item,
    suppress_item,
    pystray.Menu.SEPARATOR,
    quit_item,
)
tray_icon = pystray.Icon("Winutils", icon=icon, menu=menu)
tray_icon.run_detached()
overlay.root.mainloop()
