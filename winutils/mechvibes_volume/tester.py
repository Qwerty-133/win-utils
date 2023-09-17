import keyboard
import time

from comtypes import CLSCTX_ALL
from pycaw.pycaw import IAudioEndpointVolume
from pycaw.utils import AudioUtilities
import msvcrt


# raw_events = [(e.event_type, e.scan_code, e.name, e.time, e.device, e.modifiers, e.is_keypad) for e in keyboard.record(until='esc')]
# print(raw_events)
raw_events = [
    ("down", 35, "h", 1694795381.222214, None, None, False),
    ("up", 35, "h", 1694795381.2819862, None, None, False),
    ("down", 23, "i", 1694795381.322605, None, None, False),
    ("up", 23, "i", 1694795381.4028058, None, None, False),
    ("down", 57, "space", 1694795381.4064112, None, None, False),
    ("down", 20, "t", 1694795381.450571, None, None, False),
    ("up", 57, "space", 1694795381.4860559, None, None, False),
    ("up", 20, "t", 1694795381.5305364, None, None, False),
    ("down", 35, "h", 1694795381.5460155, None, None, False),
    ("down", 18, "e", 1694795381.5820014, None, None, False),
    ("up", 35, "h", 1694795381.618398, None, None, False),
    ("down", 19, "r", 1694795381.6508422, None, None, False),
    ("up", 18, "e", 1694795381.6742635, None, None, False),
    ("up", 19, "r", 1694795381.7345936, None, None, False),
    ("down", 18, "e", 1694795381.7396307, None, None, False),
    ("down", 57, "space", 1694795381.8025758, None, None, False),
    ("up", 18, "e", 1694795381.8299499, None, None, False),
    ("up", 57, "space", 1694795381.8740761, None, None, False),
    ("down", 20, "t", 1694795381.881775, None, None, False),
    ("down", 35, "h", 1694795381.9507062, None, None, False),
    ("up", 20, "t", 1694795381.9782076, None, None, False),
    ("up", 35, "h", 1694795382.0066469, None, None, False),
    ("down", 23, "i", 1694795382.0463133, None, None, False),
    ("down", 31, "s", 1694795382.0827072, None, None, False),
    ("up", 23, "i", 1694795382.146886, None, None, False),
    ("up", 31, "s", 1694795382.1625228, None, None, False),
    ("down", 57, "space", 1694795382.1785738, None, None, False),
    ("down", 23, "i", 1694795382.2462435, None, None, False),
    ("up", 57, "space", 1694795382.2626698, None, None, False),
    ("up", 23, "i", 1694795382.3505902, None, None, False),
    ("down", 30, "a", 1694795382.3861814, None, None, False),
    ("up", 30, "a", 1694795382.5229373, None, None, False),
    ("down", 57, "space", 1694795382.5305874, None, None, False),
    ("up", 57, "space", 1694795382.6025054, None, None, False),
    ("down", 30, "a", 1694795382.7263424, None, None, False),
    ("down", 21, "y", 1694795382.7462025, None, None, False),
    ("up", 21, "y", 1694795382.8023949, None, None, False),
    ("up", 30, "a", 1694795382.8180852, None, None, False),
    ("down", 22, "u", 1694795382.8507109, None, None, False),
    ("down", 31, "s", 1694795382.9103825, None, None, False),
    ("up", 22, "u", 1694795382.9546936, None, None, False),
    ("up", 31, "s", 1694795382.9988995, None, None, False),
    ("down", 1, "esc", 1694795383.1262157, None, None, False),
]
events = [keyboard.KeyboardEvent(*args) for args in raw_events]


def alt_tab():
    """Press and release alt+tab and then wait for a bit"""
    keyboard.press_and_release("alt+tab")
    time.sleep(0.1)


volume_set = {10: 100, 20: 68, 30: 34, 40: 24, 50: 16, 60: 12, 70: 10, 80: 8, 90: 6, 100: 5}
volume_set = {step: max(0, min(100, volume * 0.5)) for step, volume in volume_set.items()}


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

for session in AudioUtilities.GetAllSessions():
    if session.Process and session.Process.name() == "MechvibesPlusPlus.exe":
        break
else:
    raise RuntimeError("Could not find a MechvibesPlusPlus.exe session.")

print("CONTROLS: W: 10%+ S: 10%- || A: 2%- D: 2%+ || Z: 1%- X: 1%+")


try:
    while True:
        for step in [50, 40, 60, 30, 70, 20, 80, 10, 90, 100]:
            volume.SetMasterVolumeLevelScalar(step / 100, None)
            app_volume = volume_set.get(step, 100 - step)
            print(f"System volume: {step}%")

            while True:
                session.SimpleAudioVolume.SetMasterVolume(app_volume / 100, None)
                print(f"App volume: {app_volume}%", end="\r")

                alt_tab()
                keyboard.play(events)
                alt_tab()

                adjustment = msvcrt.getch().decode().lower()
                # adjustment = input().lower()
                if adjustment == "c":
                    volume_set[step] = app_volume
                    print()
                    break

                if adjustment == "w":
                    app_volume += 10
                elif adjustment == "s":
                    app_volume -= 10
                elif adjustment == "a":
                    app_volume -= 2
                elif adjustment == "d":
                    app_volume += 2
                elif adjustment == "z":
                    app_volume -= 1
                elif adjustment == "x":
                    app_volume += 1

                app_volume = max(0, min(100, app_volume))

        print("--- Current Volumes ---")
        for step, app_volume in volume_set.items():
            print(f"{step}%: {app_volume}%")
except KeyboardInterrupt:
    print(volume_set)
