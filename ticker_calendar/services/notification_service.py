from __future__ import annotations

import logging
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    from backports.zoneinfo import ZoneInfo

import requests

from ticker_calendar.config.alert_rules import MARKET_TIMEZONE
from ticker_calendar.config.server import NTFY_TOPIC, NTFY_URL

logger = logging.getLogger(__name__)


def send_ntfy(
    message: str,
    *,
    title: str = "Ticker Calendar Alert",
    topic: str | None = None,
    tags: str = "chart_with_upwards_trend",
    priority: str = "high",
) -> bool:
    topic = topic or NTFY_TOPIC
    url = f"{NTFY_URL.rstrip('/')}/{topic}"

    headers = {
        "Title": title,
        "Tags": tags,
        "Priority": priority,
    }

    try:
        response = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=15)
        if response.status_code == 200:
            logger.info("ntfy sent: %s", message[:80])
            return True
        logger.error("ntfy failed status=%s body=%s", response.status_code, response.text[:200])
        return False
    except Exception as exc:
        logger.exception("ntfy error: %s", exc)
        return False


def format_alert_message(candidate) -> str:
    timestamp = datetime.now(ZoneInfo(MARKET_TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S %Z")
    drop_line = ""
    if candidate.drop_pct is not None:
        drop_line = f"Drop: {candidate.drop_pct:.2f}%\n"

    return (
        f"{candidate.message}\n"
        f"Rule: {candidate.rule_name}\n"
        f"Ticker: {candidate.ticker}\n"
        f"{drop_line}"
        f"Time: {timestamp}"
    )
