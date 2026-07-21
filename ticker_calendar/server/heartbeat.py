import logging

from ticker_calendar.config.server import HEARTBEAT_FILE
from ticker_calendar.utils import now_iso

logger = logging.getLogger(__name__)


def write_heartbeat(status: str = "alive") -> None:
    """Write a timestamp so external monitors can verify the server is running."""
    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = now_iso()
    HEARTBEAT_FILE.write_text(f"{timestamp} {status}\n", encoding="utf-8")
    logger.debug("heartbeat: %s %s", timestamp, status)
