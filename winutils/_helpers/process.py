import subprocess
import pathlib
from winutils._helpers import path
import shlex

VIEW_COMMAND_BASE = [
    "wt",
    "--window",
    "Winutils",
    "new-tab",
    "--profile",
    "PowerShell",
    "--startingDirectory",
    path.ROOT_DIR,
    "pwsh",
    "-Command",
]


def sync_process_output(process: subprocess.Popen, file: pathlib.Path) -> None:
    """Sync the outputs of the process with a file."""
    with open(file, "wb") as f:
        for line in process.stdout:
            f.write(line)
            f.flush()


def spawn_output_view_terminal(file: pathlib.Path) -> subprocess.Popen:
    """Spawn a terminal to view the file."""
    sub_command = ["Get-Content", "-Path", str(file), "-Wait"]
    command = [*VIEW_COMMAND_BASE, shlex.join(sub_command)]

    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
