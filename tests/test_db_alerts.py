from datetime import date

import pytest

from ticker_calendar.db import alerts


pytestmark = pytest.mark.usefixtures("temp_db")

ALERT_DATE = date(2026, 7, 8)


def test_record_and_was_fired():
    assert alerts.was_fired("earnings_today", "AAPL", ALERT_DATE) is False
    record = alerts.record("earnings_today", "aapl", ALERT_DATE, "buy call")
    assert record is not None
    assert record.ticker == "AAPL"
    assert record.rule_id == "earnings_today"
    assert alerts.was_fired("earnings_today", "AAPL", ALERT_DATE) is True


def test_record_deduplicates():
    assert alerts.record("earnings_today", "AAPL", ALERT_DATE, "msg") is not None
    # UNIQUE(rule_id, ticker, alert_date) => second insert returns None.
    assert alerts.record("earnings_today", "AAPL", ALERT_DATE, "msg") is None


def test_list_recent_respects_limit():
    alerts.record("earnings_today", "AAPL", ALERT_DATE, "m1")
    alerts.record("earnings_today", "MSFT", ALERT_DATE, "m2")
    alerts.record("earnings_today", "NVDA", ALERT_DATE, "m3")
    assert len(alerts.list_recent(limit=2)) == 2
    assert len(alerts.list_recent()) == 3


def test_list_for_date_filters():
    other = date(2026, 7, 9)
    alerts.record("earnings_today", "AAPL", ALERT_DATE, "m1")
    alerts.record("earnings_today", "MSFT", other, "m2")
    for_date = alerts.list_for_date(ALERT_DATE)
    assert [r.ticker for r in for_date] == ["AAPL"]
