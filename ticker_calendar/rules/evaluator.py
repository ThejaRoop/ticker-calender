from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    from backports.zoneinfo import ZoneInfo

from ticker_calendar.config.alert_rules import (
    ALERT_MESSAGE,
    ALERT_MESSAGE_EARNINGS_MATRIX,
    ALERT_MESSAGE_MIDWEEK_EARNINGS_SETUP,
    ALERT_MESSAGE_MONTHLY_OPEX_FRIDAY,
    ALERT_MESSAGE_POST_EARNINGS_MOMENTUM,
    ALERT_MESSAGE_QUARTER_END_REBALANCE,
    ALERT_MESSAGE_NEXT_WEEK,
    ALERT_MESSAGE_TOMORROW,
    MARKET_CLOSE,
    MARKET_OPEN,
    MARKET_TIMEZONE,
    OPEX_CORE_TICKERS,
    POPULAR_FRIDAY_WATCHLIST,
    QUARTER_END_TICKERS,
    RULE_EARNINGS_DAY_MORNING_MATRIX,
    RULE_EARNINGS_NEXT_WEEK,
    RULE_EARNINGS_TODAY,
    RULE_EARNINGS_TOMORROW,
    RULE_POST_EARNINGS_MOMENTUM,
    RULE_MIDWEEK_EARNINGS_SETUP,
    RULE_POPULAR_FRIDAY,
    RULE_MONTHLY_OPEX_FRIDAY,
    RULE_QUARTER_END_REBALANCE,
    RULES_BY_ID,
)
from ticker_calendar.db import alerts as alerts_db
from ticker_calendar.db import tickers as tickers_db


@dataclass
class AlertCandidate:
    rule_id: str
    rule_name: str
    ticker: str
    message: str
    alert_date: date


def now_et() -> datetime:
    return datetime.now(ZoneInfo(MARKET_TIMEZONE))


def is_market_day(now: datetime | None = None) -> bool:
    now = now or now_et()
    if now.weekday() >= 5:
        return False
    return MARKET_OPEN <= now.time() <= MARKET_CLOSE


# Alias used by desktop UI monitor
is_market_hours = is_market_day


def _next_week_range(from_date: date) -> tuple[date, date]:
    days_until_next_monday = (7 - from_date.weekday()) % 7
    if days_until_next_monday == 0:
        days_until_next_monday = 7
    next_monday = from_date + timedelta(days=days_until_next_monday)
    next_sunday = next_monday + timedelta(days=6)
    return next_monday, next_sunday


def _prior_friday_for_next_week(from_date: date) -> date:
    next_monday, _ = _next_week_range(from_date)
    return next_monday - timedelta(days=3)


def _is_third_friday(from_date: date) -> bool:
    """Check if the given date is the third Friday of the month."""
    if from_date.weekday() != 4:  # Friday
        return False
    # Find the first Friday of the month
    first_friday = 1
    while True:
        try:
            first_friday_date = date(from_date.year, from_date.month, first_friday)
            if first_friday_date.weekday() == 4:
                break
            first_friday += 1
        except ValueError:
            return False
    # Third Friday is 14 days after first Friday
    third_friday = first_friday_date + timedelta(days=14)
    return from_date == third_friday


def _is_last_trading_day_of_month(from_date: date) -> bool:
    """Check if the given date is the last trading day of the month."""
    # Get the last day of the month
    if from_date.month == 12:
        next_month = date(from_date.year + 1, 1, 1)
    else:
        next_month = date(from_date.year, from_date.month + 1, 1)
    last_day = next_month - timedelta(days=1)
    
    # If last day is weekend, use the Friday before
    while last_day.weekday() >= 5:  # Saturday or Sunday
        last_day = last_day - timedelta(days=1)
    
    return from_date == last_day


def _should_fire(rule_id: str, ticker: str, alert_date: date) -> bool:
    return not alerts_db.was_fired(rule_id, ticker, alert_date)


def _maybe_add(
    results: list[AlertCandidate],
    rule_id: str,
    rule_name: str,
    ticker: str,
    message: str,
    alert_date: date,
) -> None:
    if not _should_fire(rule_id, ticker, alert_date):
        return
    results.append(
        AlertCandidate(
            rule_id=rule_id,
            rule_name=rule_name,
            ticker=ticker,
            message=message,
            alert_date=alert_date,
        )
    )


def evaluate_earnings_today(today: date) -> list[AlertCandidate]:
    rule = RULE_EARNINGS_TODAY
    tickers = tickers_db.get_source_earnings_on(today)
    if not tickers:
        return []

    results: list[AlertCandidate] = []
    for ticker in tickers:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
        )
    return results


def evaluate_earnings_next_week(today: date) -> list[AlertCandidate]:
    rule = RULE_EARNINGS_NEXT_WEEK
    if today.weekday() != 4:
        return []
    if today != _prior_friday_for_next_week(today):
        return []

    next_monday, next_sunday = _next_week_range(today)
    results: list[AlertCandidate] = []
    for ticker, _ in tickers_db.get_source_earnings_between(next_monday, next_sunday):
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_NEXT_WEEK.format(ticker=ticker),
            today,
        )
    return results


def evaluate_earnings_tomorrow(today: date) -> list[AlertCandidate]:
    rule = RULE_EARNINGS_TOMORROW
    tomorrow = today + timedelta(days=1)
    tickers = tickers_db.get_source_earnings_on(tomorrow)
    if not tickers:
        return []

    results: list[AlertCandidate] = []
    for ticker in tickers:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_TOMORROW.format(ticker=ticker),
            today,
        )
    return results


def evaluate_earnings_day_morning_matrix(today: date) -> list[AlertCandidate]:
    rule = RULE_EARNINGS_DAY_MORNING_MATRIX
    tickers = tickers_db.get_source_earnings_on(today)
    if not tickers:
        return []

    results: list[AlertCandidate] = []
    for ticker in tickers:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_EARNINGS_MATRIX.format(ticker=ticker),
            today,
        )
    return results


def evaluate_post_earnings_momentum(today: date) -> list[AlertCandidate]:
    """Rule 6: Post-Earnings Momentum Window (Day +1)"""
    rule = RULE_POST_EARNINGS_MOMENTUM
    # Check if yesterday was an earnings date
    yesterday = today - timedelta(days=1)
    tickers = tickers_db.get_source_earnings_on(yesterday)
    if not tickers:
        return []

    results: list[AlertCandidate] = []
    for ticker in tickers:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_POST_EARNINGS_MOMENTUM.format(ticker=ticker),
            today,
        )
    return results


def evaluate_midweek_earnings_setup(today: date) -> list[AlertCandidate]:
    """Rule 7: Mid-Week Earnings Lookahead (Wednesday Setup)"""
    rule = RULE_MIDWEEK_EARNINGS_SETUP
    if today.weekday() != 2:  # Wednesday
        return []

    # Check for earnings on Thursday or Friday of the same week
    thursday = today + timedelta(days=1)
    friday = today + timedelta(days=2)
    
    results: list[AlertCandidate] = []
    for day in [thursday, friday]:
        tickers = tickers_db.get_source_earnings_on(day)
        for ticker in tickers:
            _maybe_add(
                results,
                rule["id"],
                rule["name"],
                ticker,
                ALERT_MESSAGE_MIDWEEK_EARNINGS_SETUP.format(ticker=ticker),
                today,
            )
    return results


def evaluate_popular_friday(today: date) -> list[AlertCandidate]:
    """Rule 5: Popular Stocks Friday Watch - uses curated watchlist"""
    rule = RULE_POPULAR_FRIDAY
    if today.weekday() != 4:  # Friday
        return []

    results: list[AlertCandidate] = []
    for ticker in POPULAR_FRIDAY_WATCHLIST:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
        )
    return results


def evaluate_monthly_opex_friday(today: date) -> list[AlertCandidate]:
    """Rule 8: Monthly Options Expiration (OPEX) Friday Watch"""
    rule = RULE_MONTHLY_OPEX_FRIDAY
    if today.weekday() != 4:  # Friday
        return []
    if not _is_third_friday(today):
        return []

    results: list[AlertCandidate] = []
    for ticker in OPEX_CORE_TICKERS:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_MONTHLY_OPEX_FRIDAY.format(ticker=ticker),
            today,
        )
    return results


def evaluate_quarter_end_rebalance(today: date) -> list[AlertCandidate]:
    """Rule 9: Month-End Institutional Flow Setup"""
    rule = RULE_QUARTER_END_REBALANCE
    if not _is_last_trading_day_of_month(today):
        return []

    results: list[AlertCandidate] = []
    for ticker in QUARTER_END_TICKERS:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_QUARTER_END_REBALANCE.format(ticker=ticker),
            today,
        )
    return results


_EVALUATORS = {
    "earnings_today": evaluate_earnings_today,
    "earnings_next_week": evaluate_earnings_next_week,
    "earnings_tomorrow": evaluate_earnings_tomorrow,
    "earnings_day_morning_matrix": evaluate_earnings_day_morning_matrix,
    "post_earnings_momentum": evaluate_post_earnings_momentum,
    "midweek_earnings_setup": evaluate_midweek_earnings_setup,
    "popular_friday": evaluate_popular_friday,
    "monthly_opex_friday": evaluate_monthly_opex_friday,
    "quarter_end_rebalance": evaluate_quarter_end_rebalance,
}


def evaluate_rule(rule_id: str, now: datetime | None = None) -> list[AlertCandidate]:
    """Run a single rule. Called by the scheduler at its exact fire time."""
    now = now or now_et()
    if rule_id not in _EVALUATORS:
        raise ValueError(f"Unknown rule: {rule_id}")

    if not is_market_day(now):
        return []

    today = now.date()
    evaluator = _EVALUATORS[rule_id]
    return evaluator(today)


def evaluate_all(now: datetime | None = None) -> list[AlertCandidate]:
    """Run every rule (manual / test helper)."""
    now = now or now_et()
    candidates: list[AlertCandidate] = []
    for rule_id in RULES_BY_ID:
        candidates.extend(evaluate_rule(rule_id, now))
    return candidates