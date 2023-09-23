import typing as t
import monitorcontrol
import sys
from winutils._helpers import overlay
import customtkinter as ctk
import keyboard

INCREASE_HOTKEY = "ctrl+shift+alt+right"
DECREASE_HOTKEY = "ctrl+shift+alt+left"
BRIGHTNESS_STEP = 5
OVERLAY_TIMEOUT = 2.5

info_overlay = overlay.BottomOverlay()
info_overlay.frame.rowconfigure(0, weight=1, uniform="a")
info_overlay.frame.columnconfigure(0, weight=1, uniform="a")
info_overlay.frame.columnconfigure(1, weight=3, uniform="a")
info_overlay.frame.columnconfigure(2, weight=1, uniform="a")

brightness_double = ctk.DoubleVar()
brightness_int = ctk.IntVar()

brightness_slider = ctk.CTkProgressBar(
    info_overlay.frame, variable=brightness_double, width=0, height=5,
)
brightness_label = ctk.CTkLabel(info_overlay.frame, textvariable=brightness_int)
brightness_slider.grid(row=0, column=1, sticky="ew")
brightness_label.grid(row=0, column=2, sticky="ew")

error_overlay = overlay.BottomOverlay()
error_label = ctk.CTkLabel(error_overlay.frame, text="No monitors connected.")
error_label.pack(expand=True)


def get_fg_slider_colour() -> str:
    """Get the correct slider fg colour based on the system theme."""
    mode = ctk.get_appearance_mode()
    return "#000000" if mode == "Dark" else "#FFFFFF"


class Handler:
    """Handles the entire application logic, and houses global instances."""

    monitor: t.Optional[monitorcontrol.Monitor] = None
    brightness: t.Optional[int] = None
    running = False
    increase_hotkey = None
    decrease_hotkey = None

    @staticmethod
    def set_brightness(new_brightness: int) -> None:
        Handler.brightness = new_brightness
        brightness_double.set(new_brightness / 100)
        brightness_int.set(new_brightness)

    @staticmethod
    def display_brightness() -> None:
        """Display the current volume scale."""
        brightness_slider.configure(fg_color=get_fg_slider_colour())
        info_overlay.display(OVERLAY_TIMEOUT)

    @staticmethod
    def obtain_monitor() -> None:
        if Handler.monitor is not None:
            return

        monitors = monitorcontrol.get_monitors()
        for monitor in monitors:
            monitor.__enter__()
            if monitor.get_input_source() != monitorcontrol.InputSource.OFF:
                Handler.monitor = monitor
                brightness = monitor.get_luminance()
                brightness = round(brightness / BRIGHTNESS_STEP) * BRIGHTNESS_STEP
                Handler.set_brightness(brightness)

                return
            else:
                monitor.__exit__(*sys.exc_info())

        error_overlay.display(OVERLAY_TIMEOUT)

    @staticmethod
    def increment_brightness() -> None:
        """
        Increment the scaling factor by 1 step.

        Also notify the user of the new scaling factor.
        """
        Handler.obtain_monitor()
        if Handler.monitor is None:
            return
        new_brightness = Handler.brightness + BRIGHTNESS_STEP
        Handler.set_brightness(max(0, min(100, new_brightness)))
        Handler.adjust_monitor_brightness()
        Handler.display_brightness()

    @staticmethod
    def decrement_brightness() -> None:
        """
        Decrement the scaling factor by 1 step.

        Also notify the user of the new scaling factor.
        """
        Handler.obtain_monitor()
        if Handler.monitor is None:
            return
        new_brightness = Handler.brightness - BRIGHTNESS_STEP
        Handler.set_brightness(max(0, min(100, new_brightness)))
        Handler.adjust_monitor_brightness()
        Handler.display_brightness()

    @staticmethod
    def adjust_monitor_brightness() -> None:
        """
        Change the app volume based on the current system volume.

        The app and system volumes are inversely proportional.
        """
        Handler.obtain_monitor()
        if Handler.monitor is None:
            return
        Handler.monitor.set_luminance(Handler.brightness)

    @staticmethod
    def start(suppress: bool) -> None:
        """Listen to property changes, and hook the keyboard hotkey."""
        Handler.running = True
        Handler.sync_hooks(suppress)

    @staticmethod
    def stop() -> None:
        """Stop listening to property changes, and unhook the keyboard hotkey."""
        Handler.running = False
        if Handler.monitor is not None:
            Handler.monitor.__exit__(*sys.exc_info())
        Handler.monitor = None
        Handler.brightness = None
        Handler.cleanup_hooks()

    @staticmethod
    def cleanup_hooks() -> None:
        """Remove all exisiting keyboard hotkeys being used."""
        if Handler.increase_hotkey is not None:
            keyboard.remove_hotkey(Handler.increase_hotkey)
        if Handler.decrease_hotkey is not None:
            keyboard.remove_hotkey(Handler.decrease_hotkey)

    @staticmethod
    def sync_hooks(suppress: bool) -> None:
        """Refresh the keyboard hotkeys being used."""
        Handler.cleanup_hooks()
        Handler.increase_hotkey = keyboard.add_hotkey(
            INCREASE_HOTKEY, Handler.increment_brightness, suppress=suppress
        )
        Handler.decrease_hotkey = keyboard.add_hotkey(
            DECREASE_HOTKEY, Handler.decrement_brightness, suppress=suppress
        )

    @staticmethod
    def toggle(suppress: bool) -> None:
        """Toggle the state of the application."""
        if Handler.running:
            Handler.stop()
        else:
            Handler.start(suppress)
