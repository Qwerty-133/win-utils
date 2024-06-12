"""Execute all installs from a list file."""
import pathlib
import rich
import subprocess

app_list_source = pathlib.Path.home() / "Data" / "Backups" / "windows_apps_list.txt"
assert app_list_source.exists(), f"{app_list_source} does not exist!"

app_ids = []
for line in app_list_source.read_text().splitlines():
    if not line or line.startswith("#"):
        continue
    app_ids.append(line)

errored_app_ids = []

do_all = False
for app_id in app_ids:
    if not do_all:
        while True:
            rich.print(
                f"Install app [light_sky_blue1]{app_id}[/light_sky_blue1]?\n"
                "\\[yes (y) / no (n) / execute all (e) / quit (q)]: "
                , end=""
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

    print(f"Installing {app_id}...")
    result = subprocess.run(["winget", "install", "--id", app_id, "-e"], shell=True)
    if result.returncode != 0:
        errored_app_ids.append(app_id)
    print("\n")

if errored_app_ids:
    print("The following apps failed to install:")
    for app_id in errored_app_ids:
        rich.print(f"[red]{app_id}[/red]")
