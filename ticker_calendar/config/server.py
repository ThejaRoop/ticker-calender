import os
from pathlib import Path

# ntfy.sh push notification topic (override via env on Ubuntu server).
# ntfy.sh topics are public: anyone who knows the topic name can read your
# alerts and publish spoofed notifications. Always set NTFY_TOPIC to a long,
# random, private value in production (e.g. `openssl rand -hex 16`).
_INSECURE_DEFAULT_TOPIC = "test_myalerts"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", _INSECURE_DEFAULT_TOPIC)
NTFY_TOPIC_IS_DEFAULT = "NTFY_TOPIC" not in os.environ
NTFY_URL = os.environ.get("NTFY_URL", "https://ntfy.sh")

# Server paths (Ubuntu)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = Path(os.environ.get("TICKER_CALENDAR_LOG_DIR", PROJECT_ROOT / "logs"))
HEARTBEAT_FILE = Path(
    os.environ.get("TICKER_CALENDAR_HEARTBEAT", LOG_DIR / "heartbeat.txt")
)

# Only one alert check runs at a time (prevents overlapping yfinance calls)
JOB_LOCK_TIMEOUT_SECONDS = 600
