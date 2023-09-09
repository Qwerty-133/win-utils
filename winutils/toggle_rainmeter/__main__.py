from winutils.toggle_rainmeter import core
from winutils._helpers import toast

is_white = core.toggle_colours()
core.refresh_skins()
core.notify_state(is_white)
toast.wait_for_toast_completion()
