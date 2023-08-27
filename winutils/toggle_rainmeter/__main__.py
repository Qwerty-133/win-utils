import configparser
import pathlib
import platformdirs
import contextlib
import subprocess
import asyncio
from winutils._helpers import toast
from winutils._helpers import ini

SKIN_PATH = platformdirs.user_documents_path() / "Rainmeter" / "Skins"
MOND_PATH = SKIN_PATH / "Mond" / "@Resources" / "Variables.inc"
CLEARTEXT_PATH = SKIN_PATH / "Cleartext" / "@Resources" / "color.inc"
RAINMETER_EXECUTABLE = pathlib.Path(
    "C:/", "Program Files", "Rainmeter", "Rainmeter.exe"
)
ICON_NAME = "water-drop.ico"

is_white = False


def toggle_mond(config: configparser.ConfigParser):
    """Toggle Mond skin and update the global variable."""
    global is_white

    current = config["Variables"]["Color1"]
    if current == "0,0,0":
        config["Variables"]["Color1"] = "255,255,255"
        is_white = True
    else:
        config["Variables"]["Color1"] = "0,0,0"
        is_white = False


def toggle_cleartext(config: configparser.ConfigParser):
    """Toggle Cleartext skin."""

    current = config["Variables"]["color_opaque"]
    if current == "0,0,0,255":
        config["Variables"]["color_opaque"] = "255,255,255,255"
        config["Variables"]["color_translucent"] = "255,255,255,128"
    else:
        config["Variables"]["color_opaque"] = "0,0,0,255"
        config["Variables"]["color_translucent"] = "0,0,0,128"


def refresh_skins():
    """Refresh all skins."""
    subprocess.run([RAINMETER_EXECUTABLE, "!Refresh"])


SKINS = [
    (MOND_PATH, toggle_mond),
    (CLEARTEXT_PATH, toggle_cleartext),
]

for path, toggle in SKINS:
    with ini.edit_config(path) as config:
        toggle(config)

refresh_skins()

current_theme = "white" if is_white else "black"
asyncio.run(
    toast.show_toast(
        "Rainmeter",
        f"Toggled skin colours, currently {current_theme}.",
        icon=toast.get_icon(ICON_NAME),
    )
)
