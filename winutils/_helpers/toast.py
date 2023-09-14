import asyncio
import typing as t
import win11toast
import threading
from winutils._helpers.path import ICON_DIR

# Global
toast_future: t.Optional[asyncio.Handle] = None


def get_icon(icon_name):
    """Generate the dict for a given icon."""
    icon_path = ICON_DIR / icon_name
    assert icon_path.exists()
    return {"src": icon_path.as_uri(), "placement": "appLogoOverride"}


def show_toast(title, body, icon=None, app_id=win11toast.DEFAULT_APP_ID):
    """Show a toast notification."""
    global toast_future
    if toast_future:
        toast_future.cancel()

    toast_future = asyncio.run_coroutine_threadsafe(
        win11toast.toast_async(title, body, icon=icon, app_id=app_id), loop
    )


def initialize_thread_loop():
    """Keep the loop running in a separate thread."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


def wait_for_toast_completion():
    """Wait for the ongoing toast notification to complete."""
    if toast_future:
        toast_future.result()


loop = asyncio.new_event_loop()
thread = threading.Thread(target=initialize_thread_loop, daemon=True)
thread.start()
