import os
from pathlib import Path

# ntfy.sh push notification topic (override via env on Ubuntu server)
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "test_myalerts")
NTFY_URL = os.environ.get("NTFY_URL", "https://ntfy.sh")

# Server paths (Ubuntu)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = Path(os.environ.get("TICKER_CALENDAR_LOG_DIR", PROJECT_ROOT / "logs"))
HEARTBEAT_FILE = Path(
    os.environ.get("TICKER_CALENDAR_HEARTBEAT", LOG_DIR / "heartbeat.txt")
)

# Only one alert check runs at a time (prevents overlapping yfinance calls)
JOB_LOCK_TIMEOUT_SECONDS = 600
