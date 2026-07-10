from __future__ import annotations

import threading
from collections.abc import Callable

from ticker_calendar.config.alert_rules import POLL_INTERVAL_SECONDS
from ticker_calendar.db import alerts as alerts_db
from ticker_calendar.rules.evaluator import AlertCandidate, evaluate_all, is_market_hours


class AlertMonitor:
    def __init__(self, on_alert: Callable[[AlertCandidate], None] | None = None):
        self._on_alert = on_alert
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="AlertMonitor")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def check_now(self) -> list[AlertCandidate]:
        fired: list[AlertCandidate] = []
        for candidate in evaluate_all():
            record = alerts_db.record(
                candidate.rule_id,
                candidate.ticker,
                candidate.alert_date,
                candidate.message,
            )
            if record:
                fired.append(candidate)
                if self._on_alert:
                    self._on_alert(candidate)
        return fired

    def _run(self) -> None:
        while not self._stop.is_set():
            if is_market_hours():
                self.check_now()
            self._stop.wait(POLL_INTERVAL_SECONDS)


def get_recent_alerts(limit: int = 100):
    return alerts_db.list_recent(limit)
