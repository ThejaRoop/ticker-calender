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
    evaluate_post_earnings_momentum,
    evaluate_midweek_earnings_setup,
    evaluate_popular_friday,
    evaluate_monthly_opex_friday,
    evaluate_quarter_end_rebalance,
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


@patch("ticker_calendar.rules.evaluator.tickers_db.get_source_earnings_on")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_earnings_today_fires(mock_fired, mock_earnings_on):
    mock_earnings_on.return_value = ["AAPL"]
    today = date(2026, 7, 8)
    results = evaluate_earnings_today(today)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


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
def test_earnings_day_morning_matrix_fires(mock_fired, mock_earnings_on):
    mock_earnings_on.return_value = ["AAPL"]
    today = date(2026, 7, 8)
    results = evaluate_earnings_day_morning_matrix(today)
    assert len(results) == 1
    assert results[0].ticker == "AAPL"


@patch("ticker_calendar.rules.evaluator.tickers_db.get_source_earnings_on")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_post_earnings_momentum_fires(mock_fired, mock_earnings_on):
    """Test Rule 6: Post-Earnings Momentum Window (Day +1)"""
    # If today is 2026-07-09, yesterday is 2026-07-08
    mock_earnings_on.return_value = ["AAPL", "MSFT"]
    today = date(2026, 7, 9)
    results = evaluate_post_earnings_momentum(today)
    assert len(results) == 2
    tickers = [r.ticker for r in results]
    assert "AAPL" in tickers
    assert "MSFT" in tickers


@patch("ticker_calendar.rules.evaluator.tickers_db.get_source_earnings_on")
@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_midweek_earnings_setup_fires(mock_fired, mock_earnings_on):
    """Test Rule 7: Mid-Week Earnings Lookahead (Wednesday Setup)"""
    # Wednesday 2026-07-08, check Thursday 2026-07-09 and Friday 2026-07-10
    mock_earnings_on.side_effect = [["AAPL"], ["MSFT"]]  # Thursday, Friday
    wednesday = date(2026, 7, 8)
    results = evaluate_midweek_earnings_setup(wednesday)
    assert len(results) == 2
    tickers = [r.ticker for r in results]
    assert "AAPL" in tickers
    assert "MSFT" in tickers


@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_popular_friday_fires(mock_fired):
    """Test Rule 5: Popular Stocks Friday Watch - uses curated watchlist"""
    friday = date(2026, 7, 10)
    results = evaluate_popular_friday(friday)
    assert len(results) == 4  # MSFT, GOOGL, NVDA, SPY
    tickers = [r.ticker for r in results]
    assert "MSFT" in tickers
    assert "GOOGL" in tickers
    assert "NVDA" in tickers
    assert "SPY" in tickers


@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_monthly_opex_friday_fires(mock_fired):
    """Test Rule 8: Monthly Options Expiration (OPEX) Friday Watch"""
    # July 18, 2025 is a third Friday
    third_friday = date(2025, 7, 18)
    results = evaluate_monthly_opex_friday(third_friday)
    assert len(results) == 9  # OPEX_CORE_TICKERS count
    tickers = [r.ticker for r in results]
    assert "SPY" in tickers
    assert "QQQ" in tickers
    assert "AAPL" in tickers


@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_monthly_opex_friday_non_third_friday(mock_fired):
    """Test that OPEX rule doesn't fire on non-third Friday"""
    # July 10, 2025 is NOT the third Friday
    not_third_friday = date(2025, 7, 10)
    results = evaluate_monthly_opex_friday(not_third_friday)
    assert len(results) == 0


@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_quarter_end_rebalance_fires(mock_fired):
    """Test Rule 9: Month-End Institutional Flow Setup"""
    # June 30, 2025 is the last trading day of June 2025
    last_day = date(2025, 6, 30)
    results = evaluate_quarter_end_rebalance(last_day)
    assert len(results) == 3  # SPY, MSFT, NVDA
    tickers = [r.ticker for r in results]
    assert "SPY" in tickers
    assert "MSFT" in tickers
    assert "NVDA" in tickers


@patch("ticker_calendar.rules.evaluator.alerts_db.was_fired", return_value=False)
def test_quarter_end_rebalance_non_month_end(mock_fired):
    """Test that quarter-end rule doesn't fire on non-month-end"""
    # June 27, 2025 is NOT the last trading day
    not_last_day = date(2025, 6, 27)
    results = evaluate_quarter_end_rebalance(not_last_day)
    assert len(results) == 0


def test_now_et_has_timezone():
    assert now_et().tzinfo is not None