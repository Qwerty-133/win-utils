import keyboard
import typing as t
from winutils.mechvibes_volume import core
from winutils._helpers import overlay


class Hotkeys:
    increase: t.Optional[t.Callable] = None
    decrease: t.Optional[t.Callable] = None


def register_hotkeys() -> None:
    """Register the hotkeys for increasing/decreasing the scaling."""
    Hotkeys.increase = keyboard.add_hotkey(core.INCREASE_HOTKEY, core.Handler.increment_scaling)
    Hotkeys.decrease = keyboard.add_hotkey(core.DECREASE_HOTKEY, core.Handler.decrement_scaling)


def unregister_hotkeys() -> None:
    """Unregister the hotkeys for increasing/decreasing the scaling."""
    keyboard.remove_hotkey(Hotkeys.increase)
    keyboard.remove_hotkey(Hotkeys.decrease)


core.Handler.start_hook = register_hotkeys
core.Handler.stop_hook = unregister_hotkeys
core.Handler.start()
overlay.root.mainloop()
