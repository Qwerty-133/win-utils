######### 1 #########

import tkinter as tk
from tkinter import ttk
import typing as t
import sv_ttk
import threading
import darkdetect

root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes("-transparentcolor", "white")
root.wm_attributes("-topmost", True)
root.lift()
x_pos = root.winfo_screenwidth() // 2
y_pos = root.winfo_screenheight() // 2
root.geometry(f"+{x_pos}+{y_pos}")


class BottomOverlay:
    _previous_frame: t.Optional[tk.Frame] = None

    def __init__(self) -> None:
        self.frame = tk.Frame(root)

    def display(self, timeout: t.Optional[int]) -> None:
        if self._previous_frame is not None:
            self._previous_frame.pack_forget()
        self.frame.pack()
        if timeout is not None:
            self.frame.after(int(timeout * 1000), lambda: self.hide() or root.destroy())

    def hide(self) -> None:
        self.frame.pack_forget()


def set_sv_theme_colour(mode: str) -> None:
    """Callback for theme changes on windows, set the sv theme colour."""
    print("new", mode)
    # sv_ttk.set_theme(mode.lower())


def listen_for_theme_changes() -> None:
    """Upon being called, a thread starts which changes the sv theme."""
    thread = threading.Thread(target=darkdetect.listener, args=(set_sv_theme_colour,), daemon=True)
    thread.start()


set_sv_theme_colour(darkdetect.theme())
listen_for_theme_changes()

overlay = BottomOverlay()
volume_value = tk.IntVar()

# put this inside a canvas
canvas = tk.Canvas(overlay.frame, width=300, height=100, highlightthickness=0)

volume_slider = ttk.Progressbar(
    overlay.frame, orient=tk.HORIZONTAL, length=150, mode="determinate", variable=volume_value
)
volume_label = ttk.Label(overlay.frame, textvariable=volume_value)
# pack these both side by side, with a little bit of space
volume_slider.pack(side=tk.LEFT, padx=10)
volume_label.pack(side=tk.LEFT, padx=5)

volume_value.set(50)
overlay.display(2)
root.mainloop()


##### 2 #####

import tkinter as tk
from tkinter import ttk
import typing as t
import sv_ttk
import threading
import darkdetect

root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes("-transparentcolor", "white")
root.wm_attributes("-topmost", True)
root.wm_attributes("-disabled", True)


class Overlay:
    last_displayed_overlay: t.Optional[tk.Toplevel] = None

    def __init__(self, master) -> None:
        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)
        self.window.geometry(f"+{x_center}+{y_center}")
        self.window.after(int(timeout * 1000), lambda: self.window.destroy() or root.destroy())
        self.window.wm_attributes("-transparentcolor", "white")
        self.window.wm_attributes("-topmost", True)
        self.window.lift()
        self.window.wm_attributes("-disabled", True)

    def display(
        timeout: t.Optional[int], x: t.Optional[int] = None, y: t.Optional[int] = None
    ) -> None:
        if self.last_displayed_overlay is not None:
            self.last_displayed_overlay.destroy()
        self.last_displayed_overlay = self.window
        if x is None:
            x = screenwidth // 2
        if y is None:
            y = screenheight // 2
        self.window.geometry(f"+{x}+{y}")
        self.window.after(int(timeout * 1000), lambda: self.window.destroy() or root.destroy())


def create_overlay(master, timeout=2.5):
    # Create a themed Tkinter window
    window = tk.Toplevel(master)
    window.overrideredirect(True)
    # Position the window at the bottom of the screen
    screenwidth = master.winfo_screenwidth()
    screenheight = master.winfo_screenheight()

    x_center = screenwidth // 2
    y_center = screenheight // 2

    window.geometry(f"+{x_center}+{y_center}")
    window.after(int(timeout * 1000), lambda: window.destroy() or root.destroy())
    window.wm_attributes("-transparentcolor", "white")
    window.wm_attributes("-topmost", True)
    window.lift()
    window.wm_attributes("-disabled", True)
    return window


def set_sv_theme_colour(mode: str) -> None:
    """Callback for theme changes on windows, set the sv theme colour."""
    print("new", mode)
    sv_ttk.set_theme(mode.lower())


def listen_for_theme_changes() -> None:
    """Upon being called, a thread starts which changes the sv theme."""
    thread = threading.Thread(target=darkdetect.listener, args=(set_sv_theme_colour,), daemon=True)
    thread.start()


set_sv_theme_colour(darkdetect.theme())
listen_for_theme_changes()

overlay = create_overlay(root)
volume_value = tk.IntVar()
volume_slider = ttk.Progressbar(
    overlay, orient=tk.HORIZONTAL, length=150, mode="determinate", variable=volume_value
)
volume_label = ttk.Label(overlay, textvariable=volume_value)
# pack these both side by side, with a little bit of space
volume_slider.pack(side=tk.LEFT, padx=5)
volume_label.pack(side=tk.LEFT, padx=5)

volume_value.set(50)
root.mainloop()
