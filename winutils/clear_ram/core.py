"""The core functionality for quitting and starting certain processes.."""

from winutils._helpers import toast
import psutil
import pathlib
import platformdirs
import os

ICON_NAME = "task.ico"
EXECUTABLE_ENTRIES_PATH = (
    platformdirs.user_documents_path() / "winutils_executables.txt"
)
quit_targets = []
start_targets = []

with open(EXECUTABLE_ENTRIES_PATH) as f:
    for line in f:
        quit_target, start_target, startup_args = [
            part.strip() for part in line.split(";")
        ]
        if not start_target:
            start_target = quit_target

        quit_target = pathlib.Path(quit_target)
        start_target = pathlib.Path(start_target)

        quit_targets.append(quit_target)
        start_targets.append((start_target, startup_args))


def quit_apps():
    terminated = []

    for process in psutil.process_iter(["exe"]):
        exe = process.info["exe"]
        if exe is None:
            continue

        exe_path = pathlib.Path(exe)
        if any(exe_path == executable for executable in quit_targets):
            process.terminate()

    toast.show_toast(
        "Apps quit", f"Terminated {len(terminated)} apps.", ICON_NAME, "Clear RAM"
    )


def start_apps():
    failures = []

    for executable, args in start_targets:
        try:
            os.startfile(executable, arguments=args)
        except FileNotFoundError:
            failures.append(executable.name)

    if failures:
        message = "Could not start " + ", ".join(failures)
    else:
        message = f"Started {len(start_targets)} apps."

    toast.show_toast("Apps started", message, ICON_NAME, "Clear RAM")
