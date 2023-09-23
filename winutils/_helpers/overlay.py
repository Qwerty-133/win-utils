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
screen_x = root.winfo_screenwidth()
screen_y = root.winfo_screenheight()
width = screen_x // 10

# bottom_percent + height is 10% of screen_y, the ratio of bottom_percent/height is 1.3
# for a 1920x1080 display, 192 width 62 bottom distance 47 height
reserved_height = screen_y // 10
height = int(reserved_height // 2.3)
bottom_gap = reserved_height - height

x_pos = screen_x // 2 - width // 2
y_pos = screen_y - bottom_gap - height
root.geometry(f"{width}x{height}+{x_pos}+{y_pos}")


class BottomOverlay:
    """
    An overlay which has looks like the volume slider on Windows 11.

    While an overlay is displaying, other overlays will be hidden.
    """

    _active_overlay: t.Optional["BottomOverlay"] = None

    def __init__(self) -> None:
        self.frame = ctk.CTkFrame(root, bg_color=TRANSPARENT_COLOUR)

    def display(self, timeout: t.Optional[int] = None) -> None:
        """Display this overlay, with an optional timeout."""
        if BottomOverlay._active_overlay is None:
            root.deiconify()
        elif self is BottomOverlay._active_overlay:
            root.after_cancel(self.hide_task)
        else:
            BottomOverlay._active_overlay.hide(withdraw_root=False)

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
