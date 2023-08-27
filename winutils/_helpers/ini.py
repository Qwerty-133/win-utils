import pathlib
import contextlib
import configparser


@contextlib.contextmanager
def edit_config(path: pathlib.Path, transform: bool = False, **kwargs):
    """Context manager for editing INI files."""
    if "strict" not in kwargs:
        kwargs["strict"] = False
    if "interpolation" not in kwargs:
        kwargs["interpolation"] = None
    config = configparser.ConfigParser(**kwargs)
    if not transform:
        config.optionxform = lambda option: option

    config.read(path)

    yield config

    with open(path, "w") as configfile:
        config.write(configfile)
