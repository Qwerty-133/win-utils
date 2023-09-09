"""The core functionality for toggling the Rainmeter skin colours."""
import configparser
import pathlib
import platformdirs
import subprocess
from winutils._helpers import toast
from winutils._helpers import ini

SKIN_PATH = platformdirs.user_documents_path() / "Rainmeter" / "Skins"
MOND_PATH = SKIN_PATH / "Mond" / "@Resources" / "Variables.inc"
CLEARTEXT_PATH = SKIN_PATH / "Cleartext" / "@Resources" / "color.inc"
RAINMETER_EXECUTABLE = pathlib.Path(
    "C:/",
    "Program Files",
    "Rainmeter",
    "Rainmeter.exe",
)
ICON_NAME = "water-drop.ico"


def is_mond_white(
    config: configparser.ConfigParser,
):
    """
    Return whether the current colour being used for the skin is white.

    This function expects the Mond skin's config to be passed.
    """
    colour = config["Variables"]["color1"]
    return colour == "255,255,255"


def toggle_mond(
    config: configparser.ConfigParser,
):
    """Toggle Mond skin and update the global variable."""
    current = config["Variables"]["color1"]
    if current == "0,0,0":
        config["Variables"]["color1"] = "255,255,255"
    else:
        config["Variables"]["color1"] = "0,0,0"


def toggle_cleartext(
    config: configparser.ConfigParser,
):
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


def toggle_colours() -> bool:
    """
    Toggle the colours of all skins.

    Return whether the current colour is white.
    """
    is_white = False
    for path, toggle in SKINS:
        with ini.edit_config(path) as config:
            toggle(config)
        if path == MOND_PATH:
            is_white = is_mond_white(config)
    return is_white


def notify_state(is_white: bool) -> None:
    """Display a toast about the current skin colour being used."""
    current_theme = "white" if is_white else "black"
    toast.show_toast(
        "Rainmeter",
        f"Toggled skin colours, currently {current_theme}.",
        toast.get_icon(ICON_NAME),
        "Toggle Rainmeter",
    )
