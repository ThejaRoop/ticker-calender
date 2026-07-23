from datetime import date, datetime
from unittest.mock import patch

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    from backports.zoneinfo import ZoneInfo

import pytest

from ticker_calendar.config.alert_rules import SCHEDULED_CHECKS
from ticker_calendar.rules.evaluator import (
    evaluate_earnings_day_morning_matrix,
    evaluate_earnings_next_week,
    evaluate_earnings_today,
    evaluate_earnings_tomorrow,
    evaluate_eod_reversal,
    evaluate_friday_gamma_squeeze,
    evaluate_gap_fill_trade,
    evaluate_iv_crush,
    evaluate_monday_gap_fill,
    evaluate_popular_friday,
    evaluate_popular_weekday,
    evaluate_thursday_shakeout,
    evaluate_tuesday_high_low,
    evaluate_wednesday_midweek,
    is_market_day,
    now_et,
)
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
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_popular_weekday_fires(mock_fired, _symbols):
    wednesday = date(2026, 7, 8)
    results = evaluate_popular_weekday(wednesday)
    assert len(results) == 1
    assert results[0].ticker == "MSFT"


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
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_earnings_tomorrow_fires(mock_fired, mock_earnings_on):
    mock_earnings_on.return_value = ["AAPL"]
    today = date(2026, 7, 8)
    results = evaluate_earnings_tomorrow(today)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.tickers_db.get_source_earnings_on")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_earnings_today_fires(mock_fired, mock_earnings_on):
    mock_earnings_on.return_value = ["AAPL"]
    today = date(2026, 7, 8)
    results = evaluate_earnings_today(today)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.tickers_db.get_source_earnings_on")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_earnings_day_morning_matrix_fires(mock_fired, mock_earnings_on):
    mock_earnings_on.return_value = ["AAPL"]
    today = date(2026, 7, 8)
    results = evaluate_earnings_day_morning_matrix(today)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["MSFT"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_thursday_shakeout_fires(mock_fired, _symbols):
    thursday = date(2026, 7, 9)
    results = evaluate_thursday_shakeout(thursday)
    assert len(results) == 1
    assert results[0].ticker == "MSFT"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["NVDA"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_eod_reversal_fires(mock_fired, _symbols):
    monday = date(2026, 7, 6)
    results = evaluate_eod_reversal(monday)
    assert len(results) == 1
    assert results[0].ticker == "NVDA"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["AMD"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_gap_fill_trade_fires(mock_fired, _symbols):
    results = evaluate_gap_fill_trade(date(2026, 7, 8))
    assert len(results) == 1
    assert results[0].ticker == "AMD"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["AAPL"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_iv_crush_fires(mock_fired, _symbols):
    monday = date(2026, 7, 6)
    results = evaluate_iv_crush(monday)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["MSFT"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_monday_gap_fill_fires(mock_fired, _symbols):
    monday = date(2026, 7, 6)
    results = evaluate_monday_gap_fill(monday)
    assert len(results) == 1
    assert results[0].ticker == "MSFT"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["NVDA"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_tuesday_high_low_fires(mock_fired, _symbols):
    tuesday = date(2026, 7, 7)
    results = evaluate_tuesday_high_low(tuesday)
    assert len(results) == 1
    assert results[0].ticker == "NVDA"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["AMD"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_wednesday_midweek_fires(mock_fired, _symbols):
    wednesday = date(2026, 7, 8)
    results = evaluate_wednesday_midweek(wednesday)
    assert len(results) == 1
    assert results[0].ticker == "AMD"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["AAPL"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_friday_gamma_squeeze_fires(mock_fired, _symbols):
    friday = date(2026, 7, 10)
    results = evaluate_friday_gamma_squeeze(friday)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.get_symbols", return_value=["MSFT"])
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_popular_friday_fires(mock_fired, _symbols):
    friday = date(2026, 7, 10)
    results = evaluate_popular_friday(friday)
    assert len(results) == 1
    assert results[0].ticker == "MSFT"


def test_now_et_has_timezone():
    assert now_et().tzinfo is not None