import typing as t
import threading
from loguru import logger
import datetime
import psutil
import GPUtil
import pathlib
import time
import uuid
from winutils._helpers import process
import re

assert len(GPUtil.getGPUs()) == 1

class Threads:
    sync_thread: t.Optional[threading.Thread] = None
    sync_thread_id: t.Optional[uuid.UUID] = None
    gpu_check_thread: t.Optional[threading.Thread] = None
    ram_check_thread: t.Optional[threading.Thread] = None

SYNC_LOCK = threading.Lock()

# https://github.com/chalk/ansi-regex/blob/main/index.js
ANSI_REGEX = re.compile(
    [
		'[\\u001B\\u009B][[\\]()#;?]*(?:(?:(?:(?:;[-a-zA-Z\\d\\/#&.:=?%@~_]+)*|[a-zA-Z\\d]+(?:;[-a-zA-Z\\d\\/#&.:=?%@~_]*)*)?\\u0007)',
		'(?:(?:\\d{1,4}(?:;\\d{0,4})*)?[\\dA-PR-TZcf-nq-uy=><~]))'
	].join('|')
)

FILES_HOME = pathlib.Path.home() / "Data"
LARGE_BACKUPS = FILES_HOME / "Backups" / "Large"
SCRIPT_FILES = FILES_HOME / "Sync"

LASTSYNC_DATETIME_FORMAT = "%d %b %Y, %:%M:%S %z"
FILE_DATETIME_FORMAT = "%Y-%m-%d %H-%M-%S"
# Regular: DATETIME_FORMAT
# Large: DATETIME_FORMAT
PREVIOUS_SYNC_FILE  = SCRIPT_FILES / ".last_sync"

COMPRESSION_TARGETS = [
    ".git/",
    "node_modules/",
    "venv/",
]
SYNC_INTERVAL = 3 * 60 * 60 # 6 hours
LARGE_BACKUPS_SYNC_INTERVAL = 7 * 24 * 60 * 60 # 7 days

RAM_NEEDED = 5745
RAM_POLL_INTERVAL = 5
RAM_POLLS = 12

CPU_USAGE_THRESHOLD = 30
# Poll for 2 seconds, once every 5 seconds, 12 times (1 minute total)
CPU_POLL_INTERVAL = 5
CPU_POLL_DURATION = 2
CPU_POLLS = 12

GPU_USAGE_THRESHOLD = 30
GPU_POLL_INTERVAL = 5
GPU_POLLS = 12

POLL_FAIL_WAIT = 5 * 60


# 0 - success
# 1 - Syntax or usage error
# 2 - Error not otherwise categorised
# 3 - Directory not found
# 4 - File not found
# 5 - Temporary error (one that more retries might fix) (Retry errors)
# 6 - Less serious errors (like 461 errors from dropbox) (NoRetry errors)
# 7 - Fatal error (one that more retries won't fix, like account suspended) (Fatal errors)
# 8 - Transfer exceeded - limit set by --max-transfer reached
# 9 - Operation successful, but no files transferred
# 10 - Duration exceeded - limit set by --max-duration reached


BASE_SYNC_COMMAND = [
    "rclone",
    "--color=always",
    "sync",
    "--track-renames",
    "--fast-list",
    "--progress",
    "--verbose",
    "--metadata",
    "--create-empty-src-dirs",
    "--order-by=size,ascending",
    "--track-renames-strategy=modtime,leaf",
]

assert CPU_POLLS * CPU_POLL_INTERVAL == GPU_POLLS * GPU_POLL_INTERVAL == RAM_POLLS * RAM_POLL_INTERVAL


class BackgroundSyncHandler:
    """Handles the entire application logic, and houses global instances."""

    running = False

    @staticmethod
    def cpu_is_idle() -> bool:
        """Find whether the CPU is sufficiently idle."""
        cpu_usage = 0
        for _ in range(CPU_POLLS):
            current_cpu = psutil.cpu_percent(interval=CPU_POLL_DURATION)
            logger.trace("CPU Usage: {}%", current_cpu)
            cpu_usage += current_cpu
            time.sleep(CPU_POLL_INTERVAL - CPU_POLL_DURATION)

        logger.debug("Average CPU Usage: {}%", cpu_usage / CPU_POLLS)
        return cpu_usage / CPU_POLLS < CPU_USAGE_THRESHOLD

    @staticmethod
    def gpu_is_idle() -> bool:
        """Find whether the GPU is sufficiently idle."""
        gpu_usage = 0
        for _ in range(GPU_POLLS):
            current_gpu_usage = GPUtil.getGPUs()[0].load
            gpu_usage += current_gpu_usage
            time.sleep(GPU_POLL_INTERVAL)

        logger.debug("Average GPU Usage: {}%", gpu_usage / GPU_POLLS)
        return gpu_usage / GPU_POLLS < GPU_USAGE_THRESHOLD

    @staticmethod
    def ram_is_available() -> bool:
        """Find whether the RAM is sufficiently available."""
        ram_usage = 0
        for _ in range(RAM_POLLS):
            current_ram_usage = psutil.virtual_memory().available / (1024 ** 3)
            logger.trace("RAM Usage: {}GB", current_ram_usage)
            ram_usage += current_ram_usage 
            time.sleep(RAM_POLL_INTERVAL)

        logger.debug("Average RAM Usage: {}GB", ram_usage / RAM_POLLS)
        return ram_usage / RAM_POLLS < RAM_NEEDED

    @staticmethod
    def read_last_sync_data():
        """Read the last sync data from the file."""
        try:
            previous_sync_data = PREVIOUS_SYNC_FILE.read_text().splitlines()
        except FileNotFoundError:
            logger.info("Previous sync data not found. Creating data with defaults")
            BackgroundSyncHandler.write_last_sync_data(datetime.datetime.min, datetime.datetime.min)
            return None, None

        try:
            first_date = previous_sync_data[0].split(":", 1)[1].lstrip()
            second_date = previous_sync_data[1].split(":", 1)[1].lstrip()

            previous_regular_sync_time = datetime.datetime.strptime(first_date, LASTSYNC_DATETIME_FORMAT)
            previous_large_sync_time = datetime.datetime.strptime(second_date, LASTSYNC_DATETIME_FORMAT)

            if previous_regular_sync_time > datetime.datetime.now() or previous_large_sync_time > datetime.datetime.now():
                raise ValueError("Dates in the future")
        except ValueError:
            logger.warning("Error reading previous sync time. Resetting.")
            BackgroundSyncHandler.write_last_sync_data(datetime.datetime.min, datetime.datetime.min)
            return None, None

        return previous_regular_sync_time, previous_large_sync_time

    @staticmethod
    def write_last_sync_data(regular_sync_time: datetime.datetime, large_sync_time: datetime.datetime):
        """Write the last sync data to the file."""
        PREVIOUS_SYNC_FILE.write_text(
            f"Regular: {regular_sync_time.strftime(LASTSYNC_DATETIME_FORMAT)}\n"
            f"Large: {large_sync_time.strftime(LASTSYNC_DATETIME_FORMAT)}\n"
        )

    @staticmethod
    def sync_watch(id: uuid.UUID):
        """Queues syncs after appropriate waits."""

        previous_regular_sync_time, previous_large_sync_time = BackgroundSyncHandler.read_last_sync_data()

        while True:
            regular_sync_wait = large_sync_wait = 0

            if previous_regular_sync_time is not None:
                regular_sync_wait = SYNC_INTERVAL - (datetime.datetime.now() - previous_regular_sync_time).total_seconds()
                regular_sync_wait = max(regular_sync_wait, 0)
                logger.trace("Regular sync wait: {} seconds", regular_sync_wait)
            if previous_large_sync_time is not None:
                large_sync_wait = LARGE_BACKUPS_SYNC_INTERVAL - (datetime.datetime.now() - previous_large_sync_time).total_seconds()
                large_sync_wait = max(large_sync_wait, 0)
                logger.trace("Large sync wait: {} seconds", large_sync_wait)

            wait_required = min(regular_sync_wait, large_sync_wait)
            if wait_required > 0:
                logger.debug("Waiting for {} seconds", wait_required)
                time.sleep(wait_required)
                continue

            if Threads.sync_thread_id != id:
                logger.debug("Sync thread ID changed. Exiting.")
                break

            logger.debug("Checking resources availability")
            Threads.gpu_check_thread = threading.Thread(target=BackgroundSyncHandler.gpu_is_idle, daemon=True)
            Threads.gpu_check_thread.start()
            Threads.ram_check_thread = threading.Thread(target=BackgroundSyncHandler.ram_is_available, daemon=True)
            Threads.ram_check_thread.start()

            cpu_idle = BackgroundSyncHandler.cpu_is_idle()
            gpu_idle = Threads.gpu_check_thread.join()
            ram_available = Threads.ram_check_thread.join()

            if cpu_idle and gpu_idle and ram_available:
                Threads.gpu_check_thread = None
                Threads.ram_check_thread = None

                if Threads.sync_thread_id != id:
                    logger.debug("Sync thread ID changed after checking resources. Exiting.")
                    break

                is_regular_sync = regular_sync_wait == 0
                BackgroundSyncHandler.perform_sync(is_regular_sync=is_regular_sync)
            else:
                logger.debug("Conditions not met (CPU {}, GPU {}, RAM {}). Waiting for {} seconds.", cpu_idle, gpu_idle, ram_available, POLL_FAIL_WAIT)
                time.sleep(POLL_FAIL_WAIT)

    @staticmethod
    def _perform_sync(is_regular: bool) -> None:
        """Perform rclone sync operations (thread-unsafe)."""
        logger.info("Performing {} sync", "regular" if is_regular else "large")


    @staticmethod
    def perform_sync():
        """Perform the sync operations (thread-safe)."""
        with SYNC_LOCK:
            BackgroundSyncHandler._perform_sync()

    @staticmethod
    def start():
        """Start the backup process."""
        if BackgroundSyncHandler.running:
            logger.warning("Backup process already running.")
            return

        BackgroundSyncHandler.running = True
        logger.debug("Starting backup process.")

        Threads.sync_thread_id = uuid.uuid4()
        Threads.sync_thread = threading.Thread(
            target=BackgroundSyncHandler.sync_watch,
            args=(Threads.sync_thread_id,),
            daemon=True)
        Threads.sync_thread.start()

    @staticmethod
    def stop():
        """Stop the backup process."""
        if not BackgroundSyncHandler.running:
            logger.warning("Backup process not running.")
            return

        BackgroundSyncHandler.running = False
        logger.debug("Stopping backup process")
        Threads.sync_thread_id = None
        Threads.sync_thread = None

