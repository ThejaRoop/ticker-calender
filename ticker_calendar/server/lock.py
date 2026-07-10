from __future__ import annotations

import logging
from contextlib import contextmanager

from filelock import FileLock, Timeout

from ticker_calendar.config.server import JOB_LOCK_TIMEOUT_SECONDS, LOG_DIR

logger = logging.getLogger(__name__)

LOCK_PATH = LOG_DIR / "alert_job.lock"


@contextmanager
def job_lock(timeout: float | None = None):
    """Ensure only one alert check runs at a time (avoids overlapping yfinance calls)."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(LOCK_PATH), timeout=timeout or JOB_LOCK_TIMEOUT_SECONDS)
    acquired = False
    try:
        lock.acquire()
        acquired = True
        yield
    except Timeout:
        logger.warning("Could not acquire job lock within %ss — skipping overlapping run", timeout or JOB_LOCK_TIMEOUT_SECONDS)
        raise
    finally:
        if acquired:
            lock.release()
