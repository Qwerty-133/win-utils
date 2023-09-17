import time
from winutils.mechvibes_volume import core
import keyboard
import typing as t


class Hotkeys:
    increase: t.Optional[t.Callable] = None
    decrease: t.Optional[t.Callable] = None


def register_hotkeys() -> None:
    """Register the hotkeys for increasing/decreasing the scaling."""
    Hotkeys.increase = keyboard.add_hotkey(
        core.INCREASE_HOTKEY, core.Handler.increment_scaling, suppress=True
    )
    Hotkeys.decrease = keyboard.add_hotkey(
        core.DECREASE_HOTKEY, core.Handler.decrement_scaling, suppress=True
    )


def unregister_hotkeys() -> None:
    """Unregister the hotkeys for increasing/decreasing the scaling."""
    keyboard.remove_hotkey(Hotkeys.increase)
    keyboard.remove_hotkey(Hotkeys.decrease)


core.Handler.start_hook = register_hotkeys
core.Handler.stop_hook = unregister_hotkeys
core.Handler.start()
while True:
    time.sleep(1e6)
