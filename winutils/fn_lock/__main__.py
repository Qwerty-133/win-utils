import keyboard
from winutils.fn_lock import core

keyboard.hook(core.handle_events, suppress=True)
keyboard.wait()
