import platformdirs
import pathlib
import configparser
import sys
from winutils._helpers import toast, ini

USER_PROFILE = pathlib.Path.home()
THEME_FOLDER = platformdirs.user_data_path(appauthor="Microsoft", appname="Windows") / "Themes"
ICON_NAME = "images.ico"
THEME_NAMES = ["Light", "Dark"]

new_wallpaper_path = pathlib.Path(sys.argv[1]).resolve()
new_wallpaper_value = str(new_wallpaper_path).replace(str(USER_PROFILE), "%USERPROFILE%")

theme_files = [(THEME_FOLDER / theme).with_suffix(".theme").resolve() for theme in THEME_NAMES]


def apply_changes(config: configparser.ConfigParser) -> None:
    """Edit the wallpaper being used in the theme file."""
    config[r"Control Panel\Desktop"]["Wallpaper"] = str(new_wallpaper_value)


for theme_file in theme_files:
    with ini.edit_config(theme_file) as config:
        apply_changes(config)


toast.show_toast(
    "Theme wallpapers edited!",
    "The wallpapers for the Light and Dark themes have been edited.",
    toast.get_icon(ICON_NAME),
)
toast.wait_for_toast_completion()
