from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    from backports.zoneinfo import ZoneInfo

from ticker_calendar.config.alert_rules import (
    ALERT_MESSAGE,
    ALERT_MESSAGE_EOD_REVERSAL,
    ALERT_MESSAGE_EARNINGS_MATRIX,
    ALERT_MESSAGE_FRIDAY_GAMMA_SQUEEZE,
    ALERT_MESSAGE_GAP_FILL,
    ALERT_MESSAGE_IV_CRUSH,
    ALERT_MESSAGE_MONDAY_GAP_FILL,
    ALERT_MESSAGE_NEXT_WEEK,
    ALERT_MESSAGE_THURSDAY_SHAKEOUT,
    ALERT_MESSAGE_TOMORROW,
    ALERT_MESSAGE_TUESDAY_HIGH_LOW,
    ALERT_MESSAGE_WEDNESDAY_MIDWEEK,
    MARKET_CLOSE,
    MARKET_OPEN,
    MARKET_TIMEZONE,
    RULE_EARNINGS_DAY_MORNING_MATRIX,
    RULE_EARNINGS_NEXT_WEEK,
    RULE_EARNINGS_TODAY,
    RULE_EARNINGS_TOMORROW,
    RULE_EOD_REVERSAL,
    RULE_GAP_FILL_TRADE,
    RULE_IV_CRUSH,
    RULE_MONDAY_GAP_FILL,
    RULE_POPULAR_FRIDAY,
    RULE_POPULAR_WEEKDAY,
    RULE_THURSDAY_SHAKEOUT,
    RULE_TUESDAY_HIGH_LOW,
    RULE_WEDNESDAY_MIDWEEK,
    RULE_FRIDAY_GAMMA_SQUEEZE,
    RULES_BY_ID,
)
from ticker_calendar.db import alerts as alerts_db
from ticker_calendar.db import tickers as tickers_db
from ticker_calendar.services.popular_service import get_symbols


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


def evaluate_popular_weekday(today: date) -> list[AlertCandidate]:
    rule = RULE_POPULAR_WEEKDAY
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
        )
    return results


def evaluate_popular_friday(today: date) -> list[AlertCandidate]:
    rule = RULE_POPULAR_FRIDAY
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
        )
    return results


def evaluate_thursday_shakeout(today: date) -> list[AlertCandidate]:
    rule = RULE_THURSDAY_SHAKEOUT
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_THURSDAY_SHAKEOUT.format(ticker=ticker),
            today,
        )
    return results


def evaluate_eod_reversal(today: date) -> list[AlertCandidate]:
    rule = RULE_EOD_REVERSAL
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_EOD_REVERSAL.format(ticker=ticker),
            today,
        )
    return results


def evaluate_gap_fill_trade(today: date) -> list[AlertCandidate]:
    rule = RULE_GAP_FILL_TRADE

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_GAP_FILL.format(ticker=ticker),
            today,
        )
    return results


def evaluate_iv_crush(today: date) -> list[AlertCandidate]:
    rule = RULE_IV_CRUSH
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_IV_CRUSH.format(ticker=ticker),
            today,
        )
    return results


def evaluate_monday_gap_fill(today: date) -> list[AlertCandidate]:
    rule = RULE_MONDAY_GAP_FILL
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_MONDAY_GAP_FILL.format(ticker=ticker),
            today,
        )
    return results


def evaluate_tuesday_high_low(today: date) -> list[AlertCandidate]:
    rule = RULE_TUESDAY_HIGH_LOW
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_TUESDAY_HIGH_LOW.format(ticker=ticker),
            today,
        )
    return results


def evaluate_wednesday_midweek(today: date) -> list[AlertCandidate]:
    rule = RULE_WEDNESDAY_MIDWEEK
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_WEDNESDAY_MIDWEEK.format(ticker=ticker),
            today,
        )
    return results


def evaluate_friday_gamma_squeeze(today: date) -> list[AlertCandidate]:
    rule = RULE_FRIDAY_GAMMA_SQUEEZE
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_FRIDAY_GAMMA_SQUEEZE.format(ticker=ticker),
            today,
        )
    return results


_EVALUATORS = {
    "earnings_today": evaluate_earnings_today,
    "earnings_next_week": evaluate_earnings_next_week,
    "earnings_tomorrow": evaluate_earnings_tomorrow,
    "earnings_day_morning_matrix": evaluate_earnings_day_morning_matrix,
    "popular_weekday": evaluate_popular_weekday,
    "popular_friday": evaluate_popular_friday,
    "thursday_shakeout": evaluate_thursday_shakeout,
    "eod_reversal": evaluate_eod_reversal,
    "gap_fill_trade": evaluate_gap_fill_trade,
    "iv_crush": evaluate_iv_crush,
    "monday_gap_fill": evaluate_monday_gap_fill,
    "tuesday_high_low": evaluate_tuesday_high_low,
    "wednesday_midweek": evaluate_wednesday_midweek,
    "friday_gamma_squeeze": evaluate_friday_gamma_squeeze,
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