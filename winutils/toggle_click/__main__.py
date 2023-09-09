from winutils.toggle_click import core
from winutils._helpers import toast

new_state = core.swap_mouse_buttons()
core.notify_state(new_state)
toast.wait_for_toast_completion()
