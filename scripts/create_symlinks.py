import pathlib
import rich
import platformdirs
import os


SUBSTITUTIONS = {
    "APPDATA": platformdirs.user_data_path(roaming=True),
    "LOCALAPPDATA": platformdirs.user_data_path(),
    "HOME": pathlib.Path.home(),
    "DATA": pathlib.Path.home() / "Data",
    "DOCUMENTS": platformdirs.user_documents_path(),
    "PICTURES": platformdirs.user_pictures_path(),
    "MUSIC": platformdirs.user_music_path(),
    "VIDEOS": platformdirs.user_videos_path(),
    "DOWNLOADS": platformdirs.user_downloads_path(),
    "DESKTOP": platformdirs.user_desktop_path(),
    "PROGRAMDATA": pathlib.Path(os.environ["PROGRAMDATA"]),
    "PROGRAMFILES": pathlib.Path(os.environ["PROGRAMFILES"]),
}


links_source = pathlib.Path(SUBSTITUTIONS["DATA"] / "Backups" / "windows_symlinks.txt") # format: path/to/symlinkname path/to/target
links: list[tuple[pathlib.Path, pathlib.Path]] = []

for path in [*SUBSTITUTIONS.values(), links_source]:
    assert path.exists(), f"{path} does not exist!"

for line in links_source.read_text().splitlines():
    # skip empty lines and lines starting with "#"
    if not line or line.startswith("#"):
        continue

    symlink_path, target_path = [pathlib.Path(path.strip()) for path in line.split(";")]
    for key, value in SUBSTITUTIONS.items():
        if target_path.parts[0] == key:
            target_path = value / target_path.relative_to(key)
            break

    for key, value in SUBSTITUTIONS.items():
        if symlink_path.parts[0] == key:
            symlink_path = value / symlink_path.relative_to(key)

    assert target_path.is_absolute(), f"{target_path} is not an absolute path!"
    assert symlink_path.is_absolute(), f"{symlink_path} is not an absolute path!"
    assert target_path.exists(), f"{target_path} does not exist!"
    assert symlink_path.parent.exists(), f"{symlink_path.parent} does not exist!"

    links.append((pathlib.Path(symlink_path), pathlib.Path(target_path)))


do_all = False

def coloured_path(path: pathlib.Path) -> str:
    return f"[light_sky_blue1]{path}[/light_sky_blue1]"

# for symlink, target in links:
#     rich.print(f"[red]{symlink}[/red] [green]{target}[/green]")
# raise

for symlink, target in links:
    if symlink.exists(follow_symlinks=False) and symlink.is_symlink():
        if symlink.resolve() == target:
            rich.print(f"[yellow]Symlink already exists: {coloured_path(symlink)} -> {coloured_path(target)}[/yellow]")
        else:
            rich.print(f"[red]Symlink exists but points to {coloured_path(symlink.resolve())} instead of {coloured_path(target)}[/red]")

        continue

    if not do_all:
        while True:
            rich.print(
                f"Create symlink {coloured_path(symlink)} -> {coloured_path(target)}?\n"
                 "[plum4]\\[yes (y) / no (n) / execute all (e) / quit (q)][/plum4] ",
                end=""
            )
            choice = input().lower()
            if choice not in ["yes", "y", "no", "n", "execute all", "e", "quit", "q"]:
                print("Invalid choice!")
            else:
                break

        if choice == "q":
            break
        elif choice == "n":
            continue
        elif choice == "e":
            do_all = True


    symlink.symlink_to(target)
    rich.print(f"[green]Symlink created: {coloured_path(symlink)} -> {coloured_path(target)}[/green]")
    print()

