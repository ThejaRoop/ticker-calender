from datetime import date, datetime
from unittest.mock import patch

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    from backports.zoneinfo import ZoneInfo

import pytest

from ticker_calendar.config.alert_rules import SCHEDULED_CHECKS
from ticker_calendar.rules.evaluator import (
    AlertCandidate,
    evaluate_earnings_next_week,
    evaluate_earnings_tomorrow,
    evaluate_eod_reversal,
    evaluate_gap_fill_trade,
    evaluate_popular_weekday,
    evaluate_thursday_shakeout,
    is_market_day,
    now_et,
)
from ticker_calendar.services.notification_service import format_alert_message
from ticker_calendar.server.scheduler import list_scheduled_jobs, parse_weekdays


def test_parse_weekdays():
    assert parse_weekdays("mon,tue,wed") == "mon,tue,wed"
    assert parse_weekdays("fri") == "fri"


def test_parse_weekdays_invalid():
    with pytest.raises(ValueError):
        parse_weekdays("monday")


def test_scheduled_checks_match_list_helper():
    expected = sum(len(c["times"]) for c in SCHEDULED_CHECKS)
    assert len(list_scheduled_jobs()) == expected


def test_is_market_day_weekday_during_hours():
    dt = datetime(2026, 7, 8, 10, 0, tzinfo=ZoneInfo("America/New_York"))
    assert is_market_day(dt) is True


def test_is_market_day_weekend():
    dt = datetime(2026, 7, 11, 10, 0, tzinfo=ZoneInfo("America/New_York"))
    assert is_market_day(dt) is False


def test_is_market_day_before_open():
    dt = datetime(2026, 7, 8, 9, 0, tzinfo=ZoneInfo("America/New_York"))
    assert is_market_day(dt) is False


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["MSFT"])
@patch("ticker_calendar.rules.evaluator.get_quotes")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_popular_weekday_fires_when_down(mock_fired, mock_quotes, _symbols):
    from ticker_calendar.services.market_service import Quote

    mock_quotes.return_value = {
        "MSFT": Quote(ticker="MSFT", open_price=100.0, current_price=99.0),
    }
    wednesday = date(2026, 7, 8)
    results = evaluate_popular_weekday(wednesday)
    assert len(results) == 1
    assert results[0].ticker == "MSFT"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["MSFT"])
@patch("ticker_calendar.rules.evaluator.get_quotes")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_popular_weekday_skips_when_up(mock_fired, mock_quotes, _symbols):
    from ticker_calendar.services.market_service import Quote

    mock_quotes.return_value = {
        "MSFT": Quote(ticker="MSFT", open_price=100.0, current_price=101.0),
    }
    wednesday = date(2026, 7, 8)
    results = evaluate_popular_weekday(wednesday)
    assert results == []


def test_format_alert_message_includes_drop_percentage():
    candidate = AlertCandidate(
        rule_id="popular_weekday",
        rule_name="Popular Stocks Weekday Dip",
        ticker="MSFT",
        message="There is a chance to buy call for MSFT",
        alert_date=date(2026, 7, 8),
        drop_pct=1.0,
    )

    rendered = format_alert_message(candidate)
    assert "Drop: 1.00%" in rendered


@patch("ticker_calendar.rules.evaluator.tickers_db.get_source_earnings_between")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_earnings_next_week_prior_friday(mock_fired, mock_between):
    mock_between.return_value = [("AAPL", date(2026, 7, 13))]
    # 2026-07-10 is Friday; next Mon is 2026-07-13
    friday = date(2026, 7, 10)
    results = evaluate_earnings_next_week(friday)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.tickers_db.get_source_earnings_on")
@patch("ticker_calendar.rules.evaluator.get_quotes")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_earnings_tomorrow_dip_fires_when_down(mock_fired, mock_quotes, mock_earnings_on):
    from ticker_calendar.services.market_service import Quote

    mock_earnings_on.return_value = ["AAPL"]
    mock_quotes.return_value = {
        "AAPL": Quote(ticker="AAPL", open_price=100.0, current_price=99.0),
    }
    today = date(2026, 7, 8)
    results = evaluate_earnings_tomorrow(today)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.get_quotes")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_thursday_shakeout_fires_for_large_drop(mock_fired, mock_quotes):
    from ticker_calendar.services.market_service import Quote

    mock_quotes.return_value = {
        "MSFT": Quote(ticker="MSFT", open_price=100.0, current_price=96.0, previous_close_price=100.0),
    }
    thursday = date(2026, 7, 9)
    results = evaluate_thursday_shakeout(thursday)
    assert len(results) == 1
    assert results[0].ticker == "MSFT"


@patch("ticker_calendar.rules.evaluator.get_quotes")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_eod_reversal_fires_when_down_but_above_low(mock_fired, mock_quotes):
    from ticker_calendar.services.market_service import Quote

    mock_quotes.return_value = {
        "NVDA": Quote(ticker="NVDA", open_price=100.0, current_price=99.0, day_low_price=98.0),
    }
    monday = date(2026, 7, 6)
    results = evaluate_eod_reversal(monday)
    assert len(results) == 1
    assert results[0].ticker == "NVDA"


@patch("ticker_calendar.rules.evaluator.get_quotes")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_gap_fill_trade_fires_when_gap_down_rebounds(mock_fired, mock_quotes):
    from ticker_calendar.services.market_service import Quote

    mock_quotes.return_value = {
        "AMD": Quote(
            ticker="AMD",
            open_price=99.0,
            current_price=101.0,
            previous_close_price=100.0,
            opening_range_high=100.5,
        ),
    }
    results = evaluate_gap_fill_trade(date(2026, 7, 8))
    assert len(results) == 1
    assert results[0].ticker == "AMD"


def test_now_et_has_timezone():
    assert now_et().tzinfo is not None
