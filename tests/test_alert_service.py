import time
from datetime import date

import pytest

from ticker_calendar.rules.evaluator import AlertCandidate
from ticker_calendar.services import alert_service


pytestmark = pytest.mark.usefixtures("temp_db")


def _candidate(ticker: str) -> AlertCandidate:
    return AlertCandidate(
        rule_id="earnings_today",
        rule_name="Earnings Today",
        ticker=ticker,
        message=f"buy call for {ticker}",
        alert_date=date(2026, 7, 8),
    )


def test_check_now_records_and_invokes_callback(monkeypatch):
    monkeypatch.setattr(
        alert_service, "evaluate_all", lambda: [_candidate("AAPL"), _candidate("MSFT")]
    )
    seen = []
    monitor = alert_service.AlertMonitor(on_alert=seen.append)

    fired = monitor.check_now()

    assert {c.ticker for c in fired} == {"AAPL", "MSFT"}
    assert {c.ticker for c in seen} == {"AAPL", "MSFT"}


def test_check_now_deduplicates_across_calls(monkeypatch):
    monkeypatch.setattr(alert_service, "evaluate_all", lambda: [_candidate("AAPL")])
    monitor = alert_service.AlertMonitor()

    assert len(monitor.check_now()) == 1
    # Already recorded => alerts_db.record returns None => nothing fires again.
    assert monitor.check_now() == []


def test_get_recent_alerts(monkeypatch):
    monkeypatch.setattr(alert_service, "evaluate_all", lambda: [_candidate("AAPL")])
    alert_service.AlertMonitor().check_now()
    recent = alert_service.get_recent_alerts()
    assert [r.ticker for r in recent] == ["AAPL"]


def test_start_is_idempotent_and_stop_terminates(monkeypatch):
    monkeypatch.setattr(alert_service, "POLL_INTERVAL_SECONDS", 0.01)
    monkeypatch.setattr(alert_service, "is_market_hours", lambda: False)
    monitor = alert_service.AlertMonitor()

    monitor.start()
    first_thread = monitor._thread
    monitor.start()  # second start should not spawn a new thread
    assert monitor._thread is first_thread
    assert first_thread.is_alive()

    monitor.stop()
    first_thread.join(timeout=2)
    assert not first_thread.is_alive()


def test_run_loop_checks_during_market_hours(monkeypatch):
    monkeypatch.setattr(alert_service, "POLL_INTERVAL_SECONDS", 0.01)
    monkeypatch.setattr(alert_service, "is_market_hours", lambda: True)
    calls = []
    monkeypatch.setattr(
        alert_service.AlertMonitor, "check_now", lambda self: calls.append(1) or []
    )
    monitor = alert_service.AlertMonitor()

    monitor.start()
    time.sleep(0.05)
    monitor.stop()
    monitor._thread.join(timeout=2)

    assert calls
