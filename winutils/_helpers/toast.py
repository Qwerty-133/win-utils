import asyncio
import win11toast
from winutils._helpers.path import ICON_DIR


TIMEOUT_THRESHOLD = 1 * 1000
FALLBACK_TIMEOUT_THRESHOLD = 10 * 1000


def get_icon(icon_name):
    """Generate the dict for a given icon."""
    icon_path = ICON_DIR / icon_name
    assert icon_path.exists()
    return {
        "src": icon_path.as_uri(),
        "placement": "appLogoOverride"
    }


async def show_toast(title, body, icon=None):
    """Show a toast notification, with a fallback if the timeout is exceeded."""
    coro = win11toast.toast_async(title, body, icon=icon)

    try:
        await asyncio.wait_for(coro, timeout=TIMEOUT_THRESHOLD)
    except asyncio.TimeoutError:
        pass
    else:
        return

    fallback_coro = win11toast.toast_async(title, body)
    await asyncio.wait_for(fallback_coro, timeout=FALLBACK_TIMEOUT_THRESHOLD)
