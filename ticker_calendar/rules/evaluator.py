from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    from backports.zoneinfo import ZoneInfo

from ticker_calendar.config.alert_rules import (
    ALERT_MESSAGE,
    ALERT_MESSAGE_NEXT_WEEK,
    MARKET_CLOSE,
    MARKET_OPEN,
    MARKET_TIMEZONE,
    RULE_EARNINGS_NEXT_WEEK,
    RULE_EARNINGS_TODAY,
    RULE_POPULAR_FRIDAY,
    RULE_POPULAR_WEEKDAY,
    RULES_BY_ID,
)
from ticker_calendar.db import alerts as alerts_db
from ticker_calendar.db import tickers as tickers_db
from ticker_calendar.services.market_service import Quote, get_quotes
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
    *,
    quote: Quote | None = None,
    requires_down: bool = False,
) -> None:
    if not _should_fire(rule_id, ticker, alert_date):
        return
    if requires_down:
        if quote is None or not quote.is_down:
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


def evaluate_earnings_today(
    today: date,
    quotes: dict[str, Quote] | None = None,
) -> list[AlertCandidate]:
    rule = RULE_EARNINGS_TODAY
    tickers = tickers_db.get_source_earnings_on(today)
    if not tickers:
        return []

    if quotes is None:
        quotes = get_quotes(tickers)

    results: list[AlertCandidate] = []
    for ticker in tickers:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
            quote=quotes.get(ticker),
            requires_down=rule["requires_down"],
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
            requires_down=rule["requires_down"],
        )
    return results


def evaluate_popular_weekday(
    today: date,
    quotes: dict[str, Quote] | None = None,
) -> list[AlertCandidate]:
    rule = RULE_POPULAR_WEEKDAY
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    if quotes is None:
        quotes = get_quotes(symbols)

    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
            quote=quotes.get(ticker),
            requires_down=rule["requires_down"],
        )
    return results


def evaluate_popular_friday(
    today: date,
    quotes: dict[str, Quote] | None = None,
) -> list[AlertCandidate]:
    rule = RULE_POPULAR_FRIDAY
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    if quotes is None:
        quotes = get_quotes(symbols)

    results: list[AlertCandidate] = []
    for ticker in symbols:
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
            quote=quotes.get(ticker),
            requires_down=rule["requires_down"],
        )
    return results


_EVALUATORS = {
    "earnings_today": evaluate_earnings_today,
    "earnings_next_week": evaluate_earnings_next_week,
    "popular_weekday": evaluate_popular_weekday,
    "popular_friday": evaluate_popular_friday,
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

    if rule_id in ("earnings_today", "popular_weekday", "popular_friday"):
        return evaluator(today)
    return evaluator(today)


def evaluate_all(now: datetime | None = None) -> list[AlertCandidate]:
    """Run every rule (manual / test helper)."""
    now = now or now_et()
    candidates: list[AlertCandidate] = []
    for rule_id in RULES_BY_ID:
        candidates.extend(evaluate_rule(rule_id, now))
    return candidates
