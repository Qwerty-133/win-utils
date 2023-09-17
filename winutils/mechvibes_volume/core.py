from comtypes import CLSCTX_ALL, COMObject
from pycaw.pycaw import IAudioEndpointVolume, IAudioEndpointVolumeCallback
from pycaw.callbacks import MMNotificationClient
from pycaw.utils import AudioUtilities
import threading
import functools
import typing as t


DEBUGGING = True


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
    app_volume: int = None
    session: t.Any = None
    state_refresh_count: int = 0
    adjust_app_volume_count: int = 0

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
        # Handler.volume.RegisterControlChangeNotify(AudioEndpointVolumeCallback())
        Handler.adjust_app_volume()

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

            new_volume = 1 - system_volume
            if Handler.app_volume != new_volume:
                new_volume = min(1, max(0, new_volume))
                Handler.session.SimpleAudioVolume.SetMasterVolume(new_volume, None)
                Handler.app_volume = new_volume

    @staticmethod
    def start() -> None:
        notif_client = NotificationClient()
        enumerator = AudioUtilities.GetDeviceEnumerator()
        enumerator.RegisterEndpointNotificationCallback(notif_client)
        Handler.refresh_state()


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
