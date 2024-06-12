import rich
import pathlib
import datetime
import shlex
import subprocess
import os

DESTINATION = pathlib.Path(pathlib.Path.home() / "Data" / "Encrypted")
DESTINATION.mkdir(exist_ok=True)

command = ["bw", "export", "--format", "encrypted_json", "--output", f"{DESTINATION}{os.sep}"]
rich.print(f"Running: [bold]{shlex.join(command)}[/bold]")

subprocess.run(command, shell=True)
print()

# files are of format bitwarden_encrypted_export_yyyymmddhhmmss.json
backup_files: dict[pathlib.Path, datetime.datetime] = {
    file: datetime.datetime.strptime(file.stem.split("_")[-1], "%Y%m%d%H%M%S")
    for file in pathlib.Path(DESTINATION).glob("bitwarden_encrypted_export_*.json")
}

# keep only 5 most recent files
for file in sorted(backup_files, key=backup_files.get, reverse=True)[5:]:
    rich.print(f"[yellow]Removing: [bold]{file}[/bold][/yellow]")
    file.unlink()
    del backup_files[file]

# print available exports
print("Available backups:")
for file, date in sorted(backup_files.items(), key=lambda x: x[1], reverse=True):
    formatted_data = backup_files[file].strftime("%d %b, %Y %H:%M:%S") 
    rich.print(
        f"Backup: [blue]{formatted_data}[/blue] - [bold]{file.name}[/bold]"
    )
