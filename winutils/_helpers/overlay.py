import typing as t
import customtkinter as ctk

TRANSPARENT_COLOUR = "#000001"

root = ctk.CTk()
root.overrideredirect(True)
root.withdraw()
root.wm_attributes("-transparentcolor", TRANSPARENT_COLOUR)
root.wm_attributes("-topmost", True)
root.resizable(False, False)
root.lift()


class BottomOverlay:
    """
    An overlay which has looks like the volume slider on Windows 11.

    While an overlay is displaying, other overlays will be hidden.
    """

    _active_overlay: t.Optional["BottomOverlay"] = None

    def __init__(self) -> None:
        self.frame = ctk.CTkFrame(root, bg_color=TRANSPARENT_COLOUR)

    def adjust_window_size(self) -> None:
        """Adjust the height, width and position of the window to match the current scaling."""
        scaling = ctk.ScalingTracker.get_window_scaling(root)
        screen_x = int(root.winfo_screenwidth() * scaling)
        screen_y = int(root.winfo_screenheight() * scaling)
        width = int(screen_x // 10)
        occupied_width = int(width * scaling)

        # OUTDATED: bottom_percent + height is 10% of screen_y, the ratio of bottom_percent/height is 1.3
        # OUTDATED: for a 1920x1080 display, 192 width 62 bottom distance 47 height
        reserved_height = int((screen_y * scaling) // 10)
        widget_height = 48
        bottom_gap = reserved_height - widget_height

        x_pos = screen_x // 2 - occupied_width // 2
        y_pos = screen_y - bottom_gap - widget_height
        root.geometry(f"{width}x{widget_height}+{x_pos}+{y_pos}")


    def display(self, timeout: t.Optional[int] = None) -> None:
        """Display this overlay, with an optional timeout."""
        if BottomOverlay._active_overlay is None:
            root.deiconify()
        elif self is BottomOverlay._active_overlay:
            root.after_cancel(self.hide_task)
        else:
            BottomOverlay._active_overlay.hide(withdraw_root=False)

        self.adjust_window_size()
        self.frame.pack(fill=ctk.BOTH, expand=True)
        BottomOverlay._active_overlay = self
        if timeout is not None:
            self.hide_task = root.after(int(timeout * 1000), self.hide, True)

    def hide(self, withdraw_root: bool) -> None:
        """Hide this overlay."""
        if withdraw_root:
            root.withdraw()
        self.frame.pack_forget()
        BottomOverlay._active_overlay = None
        if self.hide_task:
            root.after_cancel(self.hide_task)
        self.hide_task = None
