import threading
import bisect
import functools
import typing as t
from comtypes import CLSCTX_ALL, COMObject
from pycaw.pycaw import IAudioEndpointVolume, IAudioEndpointVolumeCallback
from pycaw.callbacks import MMNotificationClient
from pycaw.utils import AudioUtilities
from winutils._helpers import overlay
import customtkinter as ctk

DEBUGGING = False
VOLUME_MAPPING = {
    0: 100,
    10: 100,
    20: 68,
    30: 34,
    40: 24,
    50: 16,
    60: 12,
    70: 10,
    80: 8,
    90: 6,
    100: 5,
}
SYSTEM_VOLUMES = list(VOLUME_MAPPING.keys())
APP_VOLUMES = list(VOLUME_MAPPING.values())
INCREASE_HOTKEY = "ctrl+shift+alt+up"
DECREASE_HOTKEY = "ctrl+shift+alt+down"
MIN_SCALE_FACTOR = 0
MAX_SCALE_FACTOR = 2
SCALE_FACTOR_STEP = 0.1
OVERLAY_TIMEOUT = 2.5

vol_overlay = overlay.BottomOverlay()
vol_overlay.frame.rowconfigure(0, weight=1)
vol_overlay.frame.columnconfigure(0, weight=1)
vol_overlay.frame.columnconfigure(1, weight=8)
vol_overlay.frame.columnconfigure(2, weight=1)

volume_value_double = ctk.DoubleVar()
volume_value_int = ctk.IntVar()

volume_slider = ctk.CTkProgressBar(
    vol_overlay.frame, variable=volume_value_double, width=0, height=5
)
volume_label = ctk.CTkLabel(vol_overlay.frame, textvariable=volume_value_int)
volume_slider.grid(row=0, column=1, sticky="ew")
volume_label.grid(row=0, column=2, sticky="nsew")


def get_fg_slider_colour() -> str:
    """Get the correct slider fg colour based on the system theme."""
    mode = ctk.get_appearance_mode()
    return "#000000" if mode == "Dark" else "#FFFFFF"


def debounce(callback: t.Callable, fire_after: int) -> t.Callable:
    """
    A decorator to implement debouncing.

    Whenever the function is called, after fire_after period passes, the
    callback is called. If within the period the function is called again,
    the previous timer is discared.

    The original function is still called each time.
    """

    def decorator(function: t.Callable) -> t.Callable:
        timer = None

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)

            nonlocal timer
            if timer:
                timer.cancel()
            timer = threading.Timer(fire_after, callback)
            timer.start()

        return wrapper

    return decorator


class Handler:
    """Handles the entire application logic, and houses global instances."""

    devices: t.Any
    interface: t.Any
    volume: t.Any
    notif_client: t.Any
    enumerator: t.Any
    app_volume: t.Optional[int] = None
    session: t.Any = None
    state_refresh_count = 0
    adjust_app_volume_count = 0
    scale_factor: float = 1
    running = False

    @staticmethod
    def display_scaling() -> None:
        """
        Display the current volume scale.

        We need to linearly interpolate the scale.
        """
        scale_range = MAX_SCALE_FACTOR - MIN_SCALE_FACTOR
        interpolated_value = (Handler.scale_factor - MIN_SCALE_FACTOR) / scale_range
        volume_value_int.set(round(interpolated_value * 100))
        volume_value_double.set(interpolated_value)
        volume_slider.configure(fg_color=get_fg_slider_colour())
        vol_overlay.display(OVERLAY_TIMEOUT)

    @staticmethod
    def increment_scaling() -> None:
        """
        Increment the scaling factor by 1 step.

        Also notify the user of the new scaling factor.
        """
        Handler.scale_factor += SCALE_FACTOR_STEP
        Handler.scale_factor = max(MIN_SCALE_FACTOR, min(MAX_SCALE_FACTOR, Handler.scale_factor))
        if DEBUGGING:
            print(f"Incremented scaling factor to {Handler.scale_factor}")
        Handler.adjust_app_volume()
        Handler.display_scaling()

    @staticmethod
    def decrement_scaling() -> None:
        """
        Decrement the scaling factor by 1 step.

        Also notify the user of the new scaling factor.
        """
        Handler.scale_factor -= SCALE_FACTOR_STEP
        Handler.scale_factor = max(MIN_SCALE_FACTOR, min(MAX_SCALE_FACTOR, Handler.scale_factor))
        if DEBUGGING:
            print(f"Decremented scaling factor to {Handler.scale_factor}")
        Handler.adjust_app_volume()
        Handler.display_scaling()

    @staticmethod
    def refresh_state() -> None:
        """
        Refresh the pycaw interfaces being used.

        This also calls adjust_app_volume subsequently.
        """
        if DEBUGGING:
            Handler.state_refresh_count += 1
            print(f"--- Refreshing state({Handler.state_refresh_count}) ---")

        Handler.devices = AudioUtilities.GetSpeakers()
        Handler.interface = Handler.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        Handler.volume = Handler.interface.QueryInterface(IAudioEndpointVolume)
        # Uncomment the next line to also register volume change notifiers (should be unnecessary)
        # Handler.volume.RegisterControlChangeNotify(AudioEndpointVolumeCallback())
        Handler.adjust_app_volume()

    @staticmethod
    def get_appropriate_app_volume(system_volume: float) -> float:
        """
        Get the appropriate app volume based on the system volume.

        This function linerally interpolates the current system volume.
        This function accounts for the current scale factor being used.
        """
        system_volume = round(system_volume * 100)
        index = bisect.bisect_left(SYSTEM_VOLUMES, system_volume)
        if index == 0:
            l_app_vol = 0
            l_sys_vol = 0
        else:
            l_app_vol = APP_VOLUMES[index - 1]
            l_sys_vol = SYSTEM_VOLUMES[index - 1]

        u_app_vol = APP_VOLUMES[index]
        u_sys_vol = SYSTEM_VOLUMES[index]

        app_vol_diff = u_app_vol - l_app_vol
        sys_vol_diff = u_sys_vol - l_sys_vol
        app_volume = l_app_vol + (system_volume - l_sys_vol) * app_vol_diff / sys_vol_diff

        scaled_volume = max(0, min(100, app_volume * Handler.scale_factor))
        return scaled_volume / 100

    @staticmethod
    def adjust_app_volume() -> None:
        """
        Change the app volume based on the current system volume.

        The app and system volumes are inversely proportional.
        """
        if DEBUGGING:
            Handler.adjust_app_volume_count += 1
            print(f"--- Adjusting app volume ({Handler.adjust_app_volume_count}) ---")

        if Handler.session and not Handler.session.Process.is_running():
            Handler.session = None

        if Handler.session is None:
            for session in AudioUtilities.GetAllSessions():
                if session.Process and session.Process.name() == "MechvibesPlusPlus.exe":
                    Handler.session = session
                    break

        if Handler.session is not None:
            system_volume = Handler.volume.GetMasterVolumeLevelScalar()
            if system_volume == 0:
                return

            new_volume = Handler.get_appropriate_app_volume(system_volume)
            if new_volume == Handler.app_volume:
                return
            if DEBUGGING:
                print(f"App volume changed, sys: {system_volume:%}, app: {new_volume:%}")
            Handler.session.SimpleAudioVolume.SetMasterVolume(new_volume, None)
            Handler.app_volume = new_volume

    @staticmethod
    def start() -> None:
        """Listen to property changes, and hook the keyboard hotkey."""
        Handler.running = True
        Handler.notif_client = NotificationClient()
        Handler.enumerator = AudioUtilities.GetDeviceEnumerator()
        Handler.enumerator.RegisterEndpointNotificationCallback(Handler.notif_client)
        Handler.refresh_state()
        Handler.start_hook()

    @staticmethod
    def stop() -> None:
        """Stop listening to property changes, and unhook the keyboard hotkey."""
        Handler.running = False
        Handler.enumerator.UnregisterEndpointNotificationCallback(Handler.notif_client)
        Handler.stop_hook()

    @staticmethod
    def toggle() -> None:
        """Toggle the state of the application."""
        if Handler.running:
            Handler.stop()
        else:
            Handler.start()

    @staticmethod
    def start_hook() -> None:
        """Perform post-setup actions, meant to be reassigned."""

    @staticmethod
    def stop_hook() -> None:
        """Perform post-teardown actions, meant to be reassigned."""


class NotificationClient(MMNotificationClient):
    """Sends events for device property changes."""

    @debounce(Handler.refresh_state, 0.1)
    def on_property_value_changed(self, *args, **kwargs):
        """
        This method runs whenever the property of a device changes.

        When this method fires, the volume handler should be refreshed.
        This method is debounced to prevent frequent refreshes.
        """
        if DEBUGGING:
            print("Property changed", args, kwargs)


class AudioEndpointVolumeCallback(COMObject):
    """
    Calls adjust_app_volume upon volume changes.

    Currently disabled.
    """

    _com_interfaces_ = [IAudioEndpointVolumeCallback]

    @debounce(Handler.adjust_app_volume, 0.1)
    def OnNotify(self, pNotify):
        """Adjust the volume of Mechvibes, after debouncing bursts under .1s"""
        if DEBUGGING:
            print("Notifying", self, pNotify)
