import typing as t
import customtkinter as ctk

root = ctk.CTk()
root.overrideredirect(True)
root.withdraw()
root.wm_attributes("-transparentcolor", "#000001")
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
        self.frame = ctk.CTkFrame(root, bg_color="#000001")

    def display(self, timeout: t.Optional[int] = None) -> None:
        """Display this overlay, with an optional timeout."""
        if self._active_overlay is None:
            root.deiconify()
        elif self is self._active_overlay:
            root.after_cancel(self.hide_task)
        else:
            self._active_overlay.hide()

        self.frame.pack(fill=ctk.BOTH, expand=True)
        self._active_overlay = self
        if timeout is not None:
            self.hide_task = root.after(int(timeout * 1000), self.hide)

    def hide(self) -> None:
        """Hide this overlay."""
        root.withdraw()
        self.frame.pack_forget()
        self._active_overlay = None
        self.hide_task = None
