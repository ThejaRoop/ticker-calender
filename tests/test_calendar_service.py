from datetime import timedelta

import pytest

from ticker_calendar.config.settings import CALENDAR_END, CALENDAR_START, RECURRENCE_DAYS
from ticker_calendar.services import calendar_service
from ticker_calendar.db import tickers


pytestmark = pytest.mark.usefixtures("temp_db")


def test_recurrence_dates_steps_by_recurrence_days_within_range():
    dates = calendar_service.recurrence_dates(CALENDAR_START)
    assert dates[0] == CALENDAR_START
    assert len(dates) >= 2
    for prev, curr in zip(dates, dates[1:]):
        assert (curr - prev).days == RECURRENCE_DAYS
    assert all(d <= CALENDAR_END for d in dates)


def test_recurrence_dates_single_when_near_end():
    near_end = CALENDAR_END - timedelta(days=RECURRENCE_DAYS - 1)
    assert calendar_service.recurrence_dates(near_end) == [near_end]


def test_add_ticker_with_recurrence_adds_series():
    added, skipped = calendar_service.add_ticker_with_recurrence("aapl", CALENDAR_START)
    assert skipped == []
    assert len(added) == len(calendar_service.recurrence_dates(CALENDAR_START))
    assert all(e.ticker == "AAPL" for e in added)


def test_add_ticker_with_recurrence_skips_existing():
    # Pre-create the first occurrence so it gets skipped on the recurrence run.
    tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    added, skipped = calendar_service.add_ticker_with_recurrence("AAPL", CALENDAR_START)
    assert CALENDAR_START in skipped
    assert CALENDAR_START not in [e.entry_date for e in added]


def test_update_ticker_delegates():
    entry = tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    updated = calendar_service.update_ticker(entry.id, "MSFT")
    assert updated.ticker == "MSFT"


def test_delete_ticker_missing_returns_zero():
    assert calendar_service.delete_ticker(999999) == 0


def test_delete_ticker_single():
    entry = tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    assert calendar_service.delete_ticker(entry.id) == 1
    assert tickers.get_entry(entry.id) is None


def test_delete_ticker_series_when_on_source_date():
    calendar_service.add_ticker_with_recurrence("AAPL", CALENDAR_START)
    source_entry = tickers.get_entries_for_date(CALENDAR_START)[0]
    deleted = calendar_service.delete_ticker(source_entry.id, delete_series=True)
    assert deleted >= 2
    assert tickers.get_entries_for_date(CALENDAR_START) == []


def test_delete_ticker_series_ignored_when_not_source_date():
    d2 = CALENDAR_START + timedelta(days=3)
    tickers.add_ticker("AAPL", d2, CALENDAR_START)
    entry = tickers.get_entries_for_date(d2)[0]
    # entry_date != source_date, so only this row is deleted despite delete_series=True.
    assert calendar_service.delete_ticker(entry.id, delete_series=True) == 1


def test_get_month_data_and_day_entries():
    tickers.add_ticker("AAPL", CALENDAR_START, CALENDAR_START)
    month = calendar_service.get_month_data(CALENDAR_START.year, CALENDAR_START.month)
    assert month[CALENDAR_START][0].ticker == "AAPL"
    day = calendar_service.get_day_entries(CALENDAR_START)
    assert [e.ticker for e in day] == ["AAPL"]
