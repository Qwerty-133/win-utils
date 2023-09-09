from pynput import keyboard
import asyncio
from winutils._helpers import toast


ICON_NAME = "function.ico"
HOTKEY = "<cmd>+`"
controller = keyboard.Controller()


FN_KEY_MAPPING = {
    keyboard.Key.f6: keyboard.Key.media_previous,
    keyboard.Key.f7: keyboard.Key.media_play_pause,
    keyboard.Key.f8: keyboard.Key.media_next,
    keyboard.Key.f10: keyboard.Key.media_volume_down,
    keyboard.Key.f11: keyboard.Key.media_volume_up,
    keyboard.Key.f12: keyboard.Key.media_volume_mute,
}


def toggle_enabled():
    global enabled
    enabled = not enabled
    status = "enabled" if enabled else "disabled"
    asyncio.run(
        toast.show_toast(
            f"Fn-lock toggled. Currently: {status}",
            toast.get_icon(ICON_NAME),
        )
    )
    print(status)


def on_press(key):
    hotkey.press(listener.canonical(key))
    if not enabled:
        return

    if key in FN_KEY_MAPPING:
        print("pressing")
        controller.tap(FN_KEY_MAPPING[key])
        return 1


def on_release(key):
    hotkey.release(listener.canonical(key))


hotkey = keyboard.HotKey(keyboard.HotKey.parse(HOTKEY), toggle_enabled)
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
