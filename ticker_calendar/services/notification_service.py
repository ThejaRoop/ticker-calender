from __future__ import annotations

import logging
from datetime import datetime

import requests

from ticker_calendar.config.server import NTFY_TOPIC, NTFY_TOPIC_IS_DEFAULT, NTFY_URL

logger = logging.getLogger(__name__)

_warned_insecure_topic = False


def _warn_insecure_topic_once(topic: str) -> None:
    global _warned_insecure_topic
    if _warned_insecure_topic:
        return
    _warned_insecure_topic = True
    logger.warning(
        "Using the built-in default ntfy topic %r. ntfy.sh topics are public: "
        "anyone who knows this name can read your alerts and send spoofed "
        "notifications. Set the NTFY_TOPIC env var to a private random value.",
        topic,
    )


def send_ntfy(
    message: str,
    *,
    title: str = "Ticker Calendar Alert",
    topic: str | None = None,
    tags: str = "chart_with_upwards_trend",
    priority: str = "high",
) -> bool:
    topic = topic or NTFY_TOPIC
    if NTFY_TOPIC_IS_DEFAULT and topic == NTFY_TOPIC:
        _warn_insecure_topic_once(topic)
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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    drop_line = ""
    if getattr(candidate, "drop_pct", None) is not None:
        drop_line = f"Drop: {candidate.drop_pct:.2f}%\n"

    return (
        f"{candidate.message}\n"
        f"Rule: {candidate.rule_name}\n"
        f"Ticker: {candidate.ticker}\n"
        f"{drop_line}"
        f"Time: {timestamp}"
    )
