# Clear RAM

This tool quits certain processes to free up RAM.
The processes can be started again later.

## Usage

### File Format

First, a file needs to be created in the documents folder (Win+R, type `shell:documents`).
The file should be named `winutils_executables.txt` and contain one process on each line.

The format is `path_to_process_to_be_quit.exe; path_to_process_to_be_started.exe; arguments`,
example: `C:\Program Files\Microsoft Office\root\Office16\ONENOTE.EXE; C:\Program Files\Microsoft Office\root\Office16\ONENOTE.EXE; /background`.

`path_to_process_to_be_started.exe` can be left blank to use the same path as `path_to_process_to_be_quit.exe`.

### Running

To quit the processes run the [`__main__.py`](__main__.py) Python script.\
To start the processes again run `__main__.py -s`.

