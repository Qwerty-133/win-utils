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
from winutils.monitor_brightness import core as monitor_core
from winutils.clear_ram import core as clear_ram_core
from winutils._helpers import path, overlay
from PIL import Image

ICON_PATH = path.ICON_DIR / "settings.ico"
CLICK_HOTKEY = "ctrl+alt+shift+c"
RAIN_HOTKEY = "ctrl+alt+shift+r"
RAM_HOTKEY = "ctrl+alt+shift+t"
CONFIG_PATH = platformdirs.user_config_path("Winutils", appauthor=False)
SETTINGS_PATH = CONFIG_PATH / "settings.json"

ram_next_action_is_quit = True

def invoke_ram_toggle() -> None:
    """Run the clear ram tool."""
    global ram_next_action_is_quit
    if ram_next_action_is_quit:
        clear_ram_core.quit_apps()
    else:
        clear_ram_core.start_apps()
    ram_next_action_is_quit = not ram_next_action_is_quit


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
    """
    Invoke the original toggle_enabled function, and update the menu item.

    The current state is also saved into the settings.
    """
    original_toggle_enabled()
    tray_icon.update_menu()
    settings["fn_lock_enabled"] = fn_core.State.enabled
    SETTINGS_PATH.write_text(json.dumps(settings))


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


def toggle_monitor_brightness() -> None:
    """Toggle the monitor brightness tool."""
    monitor_core.Handler.toggle(suppress=settings["suppressive_key_events"])
    settings["monitor_brightness_enabled"] = monitor_core.Handler.running
    SETTINGS_PATH.write_text(json.dumps(settings))


class Hooks:
    """Store keyboard hooks used by this tool."""

    fn_hook = None
    click_hotkey = None
    rain_hotkey = None
    ram_hotkey = None
    increase_mech_hotkey = None
    decrease_mech_hotkey = None


def initialize_hooks() -> None:
    """
    Start all keyboard hooks, keeping in mind the suppression configuration.
    """
    if settings["suppressive_key_events"]:
        Hooks.fn_hook = keyboard.hook(fn_core.handle_events, suppress=True)
        Hooks.click_hotkey = keyboard.add_hotkey(CLICK_HOTKEY, invoke_click, suppress=True)
        Hooks.rain_hotkey = keyboard.add_hotkey(RAIN_HOTKEY, invoke_rainmeter, suppress=True)
        Hooks.ram_hotkey = keyboard.add_hotkey(RAM_HOTKEY, invoke_ram_toggle, suppress=True)
    else:
        Hooks.click_hotkey = keyboard.add_hotkey(CLICK_HOTKEY, invoke_click)
        Hooks.rain_hotkey = keyboard.add_hotkey(RAIN_HOTKEY, invoke_rainmeter)
        Hooks.ram_hotkey = keyboard.add_hotkey(RAM_HOTKEY, invoke_ram_toggle)


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
    keyboard.remove_hotkey(Hooks.ram_hotkey)
    Hooks.ram_hotkey = None

    if settings["mechvibes_enabled"]:
        mech_stop_hook()
        mech_start_hook()
    if settings["monitor_brightness_enabled"]:
        monitor_core.Handler.sync_hooks(suppress=settings["suppressive_key_events"])

    initialize_hooks()


def teardown_app() -> None:
    """Teardown the application."""
    tray_icon.stop()
    overlay.root.after(1, overlay.root.destroy)


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
    settings = {
        "suppressive_key_events": False,
        "fn_lock_enabled": False,
        "mechvibes_enabled": False,
        "monitor_brightness_enabled": False,
    }
if settings["mechvibes_enabled"]:
    mech_core.Handler.start()
if settings["monitor_brightness_enabled"]:
    monitor_core.Handler.start(suppress=settings["suppressive_key_events"])
fn_core.State.enabled = settings["fn_lock_enabled"]

initialize_hooks()

icon = Image.open(ICON_PATH)
icon.size = (64, 64)

click_item = pystray.MenuItem("Swap mouse buttons", invoke_click)
rain_item = pystray.MenuItem("Toggle Rainmeter colours", invoke_rainmeter)
fn_lock_item = pystray.MenuItem(
    "Fn Lock",
    original_toggle_enabled,
    checked=lambda item: fn_core.State.enabled,
    enabled=lambda item: settings["suppressive_key_events"],
)
fn_lock_item
mechvibes_item = pystray.MenuItem(
    "Mechvibes stable audio",
    mech_core.Handler.toggle,
    checked=lambda item: mech_core.Handler.running,
)
monitor_item = pystray.MenuItem(
    "Monitor brightness",
    toggle_monitor_brightness,
    checked=lambda item: monitor_core.Handler.running,
)

quit_apps_item = pystray.MenuItem("Quit target apps", clear_ram_core.quit_apps)
start_apps_item = pystray.MenuItem("Start target apps", clear_ram_core.start_apps)

suppress_item = pystray.MenuItem(
    "Use suppressive events",
    change_key_supression,
    checked=lambda item: settings["suppressive_key_events"],
)
quit_item = pystray.MenuItem("Quit", teardown_app)

menu = pystray.Menu(
    click_item,
    rain_item,
    fn_lock_item,
    mechvibes_item,
    monitor_item,
    pystray.Menu.SEPARATOR,
    start_apps_item,
    quit_apps_item,
    pystray.Menu.SEPARATOR,
    suppress_item,
    quit_item,
)
tray_icon = pystray.Icon("Winutils", icon=icon, menu=menu)
tray_icon.run_detached()

try:
    overlay.root.mainloop()
except KeyboardInterrupt:
    teardown_app()
