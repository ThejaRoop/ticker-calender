from datetime import date, timedelta

import pytest

from ticker_calendar.config.settings import CALENDAR_END, CALENDAR_START
from ticker_calendar.db import tickers


pytestmark = pytest.mark.usefixtures("temp_db")


def test_add_ticker_normalizes_and_returns_entry():
    entry = tickers.add_ticker("  aapl ", CALENDAR_START, CALENDAR_START)
    assert entry is not None
    assert entry.ticker == "AAPL"
    assert entry.entry_date == CALENDAR_START
    assert entry.source_date == CALENDAR_START
    assert entry.id > 0


def test_add_ticker_rejects_empty_ticker():
    assert tickers.add_ticker("   ", CALENDAR_START, CALENDAR_START) is None


def test_add_ticker_rejects_out_of_range_dates():
    before = CALENDAR_START - timedelta(days=1)
    after = CALENDAR_END + timedelta(days=1)
    assert tickers.add_ticker("AAPL", before, before) is None
    assert tickers.add_ticker("AAPL", after, after) is None


def test_add_ticker_rejects_duplicate():
    assert tickers.add_ticker("MSFT", CALENDAR_START, CALENDAR_START) is not None
    # Same ticker + entry_date violates the UNIQUE constraint.
    assert tickers.add_ticker("msft", CALENDAR_START, CALENDAR_START) is None


def test_get_entry_found_and_missing():
    entry = tickers.add_ticker("NVDA", CALENDAR_START, CALENDAR_START)
    assert tickers.get_entry(entry.id).ticker == "NVDA"
    assert tickers.get_entry(999999) is None


def test_get_entries_for_date_orders_by_ticker():
    tickers.add_ticker("ZM", CALENDAR_START, CALENDAR_START)
    tickers.add_ticker("AMD", CALENDAR_START, CALENDAR_START)
    entries = tickers.get_entries_for_date(CALENDAR_START)
    assert [e.ticker for e in entries] == ["AMD", "ZM"]


def test_get_entries_for_month_groups_by_date():
    day1 = CALENDAR_START
    day2 = CALENDAR_START + timedelta(days=1)
    tickers.add_ticker("AAPL", day1, day1)
    tickers.add_ticker("MSFT", day2, day2)
    result = tickers.get_entries_for_month(day1.year, day1.month)
    assert result[day1][0].ticker == "AAPL"
    assert result[day2][0].ticker == "MSFT"


def test_get_entries_for_month_handles_december_boundary():
    # Exercises the month == 12 -> next-year rollover branch without error.
    assert tickers.get_entries_for_month(CALENDAR_START.year, 12) == {}


def test_get_source_earnings_on_returns_source_day_tickers():
    tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    # entry_date != source_date, so it is NOT a source-day earning.
    other = CALENDAR_START + timedelta(days=5)
    tickers.add_ticker("MSFT", other, CALENDAR_START)
    assert tickers.get_source_earnings_on(CALENDAR_START) == ["AAPL"]


def test_get_source_earnings_between_filters_range():
    d1 = CALENDAR_START
    d2 = CALENDAR_START + timedelta(days=2)
    outside = CALENDAR_START + timedelta(days=10)
    tickers.add_ticker("AAPL", d1, d1)
    tickers.add_ticker("MSFT", d2, d2)
    tickers.add_ticker("NVDA", outside, outside)
    result = tickers.get_source_earnings_between(d1, d2)
    assert result == [("AAPL", d1), ("MSFT", d2)]


def test_update_ticker_success():
    entry = tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    updated = tickers.update_ticker(entry.id, " tsla ")
    assert updated is not None
    assert updated.ticker == "TSLA"


def test_update_ticker_rejects_empty():
    entry = tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    assert tickers.update_ticker(entry.id, "  ") is None


def test_update_ticker_missing_entry():
    assert tickers.update_ticker(999999, "AAPL") is None


def test_update_ticker_duplicate_conflict():
    e1 = tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    tickers.add_ticker("MSFT", CALENDAR_START, CALENDAR_START)
    # Renaming AAPL -> MSFT on the same date collides with the UNIQUE constraint.
    assert tickers.update_ticker(e1.id, "MSFT") is None


def test_delete_ticker():
    entry = tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    assert tickers.delete_ticker(entry.id) is True
    assert tickers.delete_ticker(entry.id) is False


def test_delete_ticker_series_removes_all_recurrences():
    d1 = CALENDAR_START
    d2 = CALENDAR_START + timedelta(days=3)
    tickers.add_ticker("AAPL", d1, d1)
    tickers.add_ticker("AAPL", d2, d1)
    deleted = tickers.delete_ticker_series(d1, "aapl")
    assert deleted == 2
    assert tickers.get_entries_for_date(d1) == []
    assert tickers.get_entries_for_date(d2) == []
