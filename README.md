<!-- markdownlint-disable-next-line first-line-heading -->
<div align="center">
  <h1>Winutils</h1>
  A simple and easy to use Windows tray tool having various utilities.
</div>

<p align="center">
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/Qwerty-133/win-utils">
  </a>
  <a href="commits">
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/Qwerty-133/win-utils">
  </a>
</p>

This is a mono-repository for a bunch of utilities I use on Windows.\
The README of [each tool subdirectory](winutils/) has more information on each particular tool.

> :warning: Scripts (currently) may use hardcoded values, and thus may not work properly on your machine. Scripts are also not
> designed to be easily configurable.

## Demonstration

<!-- assets/demos/App Runner.gif assets/demos/Monitor Brightness.gif assets/demos/Tray Tool.png -->

![App Runner](assets/demos/App%20Runner.gif)
![Monitor Brightness](assets/demos/Monitor%20Brightness.gif)
![Tray Tool](assets/demos/Tray%20Tool.png)

## Utility List

- [App Runner](winutils/clear_ram/): Stop and start certain application groups with a single click
- [Fn Lock](winutils/fn_lock/): Simulate function lock key functionality for keyboards that don't have it
- [Mechvibes Volume](winutils/mechvibes_volume/): Normalize volume levels for the Mechvibes application relative to the system volume
- [Monitor Brightness](winutils/monitor_brightness/): Control external monitor brightness with shortcuts
- [Theme Wallpaper Editor](winutils/set_wallpapers/): Set a new wallpaper for the "Dark" and "Light" windows themes
- [Sync](winutils/sync/): (Under Development) Uses Rclone to backup files regularly
- [Toggle Click](winutils/toggle_click/): Toggle the mouse primary button with a single click
- [Toggle Rainmeter Skin](winutils/toggle_rainmeter/): Switch between light and dark Rainmeter skins
- [Utility Manager](winutils/utility_manager/): A tray tool to access all the various utilities

## Script List

This repository also contains a few standalone scripts that are not part of the tray tool.

- [Backup Bitwarden](scripts/backup_bitwarden.py): Maintain up to 5 encrypted Bitwarden backups
- [Create Symlinks](scripts/create_symlinks.py): Create symlinks as per a config file to particular directories
- [WinGet App Installer](scripts/winget_bulk_installer.py): Bulk install apps as per a config file using WinGet

## Building

Builds are made using PyInstaller, and the following command can be used to build the main tray tool as a console-less executable.

```sh
python -m PyInstaller winutils/utility_manager/__main__.py \
--noconsole
--icon "icons/settings.ico"
--name Winutils
--add-data "icons;icons"
```

The additional `--onefile` flag can be supplied to create a single executable file.

> If you are running MacOS, you may use the `--target-architecture` flag to choose between `x86` and `x64` or universal binaries.

You may also build an individual utility by changing the path in the above command, you may also want to use the icon corresponding to that utility.
