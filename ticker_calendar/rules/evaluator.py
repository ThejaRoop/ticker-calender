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
    ALERT_MESSAGE_GAP_FILL,
    ALERT_MESSAGE_NEXT_WEEK,
    ALERT_MESSAGE_THURSDAY_SHAKEOUT,
    ALERT_MESSAGE_TOMORROW,
    MARKET_CLOSE,
    MARKET_OPEN,
    MARKET_TIMEZONE,
    RULE_EARNINGS_NEXT_WEEK,
    RULE_EARNINGS_TODAY,
    RULE_EARNINGS_TOMORROW,
    RULE_EOD_REVERSAL,
    RULE_GAP_FILL_TRADE,
    RULE_POPULAR_FRIDAY,
    RULE_POPULAR_WEEKDAY,
    RULE_THURSDAY_SHAKEOUT,
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
    drop_pct: float | None = None


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
    condition=None,
    drop_pct: float | None = None,
) -> None:
    if not _should_fire(rule_id, ticker, alert_date):
        return
    if requires_down:
        if quote is None or not quote.is_down:
            return
    if condition is not None:
        if quote is None or not condition(quote):
            return
    results.append(
        AlertCandidate(
            rule_id=rule_id,
            rule_name=rule_name,
            ticker=ticker,
            message=message,
            alert_date=alert_date,
            drop_pct=drop_pct,
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
        quote = quotes.get(ticker)
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
            quote=quote,
            requires_down=rule["requires_down"],
            drop_pct=_drop_pct(quote),
        )
    return results


def evaluate_earnings_next_week(today: date) -> list[AlertCandidate]:
    rule = RULE_EARNINGS_NEXT_WEEK
    if today.weekday() != 4:
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


def evaluate_earnings_tomorrow(
    today: date,
    quotes: dict[str, Quote] | None = None,
) -> list[AlertCandidate]:
    rule = RULE_EARNINGS_TOMORROW
    tomorrow = today + timedelta(days=1)
    tickers = tickers_db.get_source_earnings_on(tomorrow)
    if not tickers:
        return []

    if quotes is None:
        quotes = get_quotes(tickers)

    results: list[AlertCandidate] = []
    for ticker in tickers:
        quote = quotes.get(ticker)
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_TOMORROW.format(ticker=ticker),
            today,
            quote=quote,
            requires_down=rule["requires_down"],
            drop_pct=_drop_pct(quote),
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
        quote = quotes.get(ticker)
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
            quote=quote,
            requires_down=rule["requires_down"],
            drop_pct=_drop_pct(quote),
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
        quote = quotes.get(ticker)
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE.format(ticker=ticker),
            today,
            quote=quote,
            requires_down=rule["requires_down"],
            drop_pct=_drop_pct(quote),
        )
    return results


def _drop_pct(quote: Quote | None) -> float | None:
    """Percent decline from the day's open. Only meaningful when the stock is
    actually below its open, so non-positive values return None."""
    if quote is None:
        return None
    if quote.open_price in (None, 0) or quote.current_price is None:
        return None
    pct = round(((quote.open_price - quote.current_price) / quote.open_price) * 100, 2)
    return pct if pct > 0 else None


def evaluate_thursday_shakeout(
    today: date,
    quotes: dict[str, Quote] | None = None,
) -> list[AlertCandidate]:
    rule = RULE_THURSDAY_SHAKEOUT
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    if quotes is None:
        quotes = get_quotes(symbols)

    results: list[AlertCandidate] = []
    for ticker in symbols:
        quote = quotes.get(ticker)
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_THURSDAY_SHAKEOUT.format(ticker=ticker),
            today,
            quote=quote,
            condition=lambda quote: (
                quote.previous_close_price is not None
                and quote.current_price is not None
                and quote.previous_close_price > 0
                and (quote.previous_close_price - quote.current_price) / quote.previous_close_price > 0.015
            ),
        )
    return results


def evaluate_eod_reversal(
    today: date,
    quotes: dict[str, Quote] | None = None,
) -> list[AlertCandidate]:
    rule = RULE_EOD_REVERSAL
    if today.weekday() not in rule["weekdays"]:
        return []

    symbols = get_symbols()
    if quotes is None:
        quotes = get_quotes(symbols)

    results: list[AlertCandidate] = []
    for ticker in symbols:
        quote = quotes.get(ticker)
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_EOD_REVERSAL.format(ticker=ticker),
            today,
            quote=quote,
            condition=lambda quote: (
                quote.is_down
                and quote.day_low_price is not None
                and quote.current_price is not None
                and quote.current_price > quote.day_low_price
            ),
            drop_pct=_drop_pct(quote),
        )
    return results


def evaluate_gap_fill_trade(
    today: date,
    quotes: dict[str, Quote] | None = None,
) -> list[AlertCandidate]:
    rule = RULE_GAP_FILL_TRADE

    symbols = get_symbols()
    if quotes is None:
        quotes = get_quotes(symbols)

    results: list[AlertCandidate] = []
    for ticker in symbols:
        quote = quotes.get(ticker)
        _maybe_add(
            results,
            rule["id"],
            rule["name"],
            ticker,
            ALERT_MESSAGE_GAP_FILL.format(ticker=ticker),
            today,
            quote=quote,
            condition=lambda quote: (
                quote.previous_close_price is not None
                and quote.open_price is not None
                and quote.opening_range_high is not None
                and quote.current_price is not None
                and quote.open_price < quote.previous_close_price
                and quote.current_price >= quote.opening_range_high
            ),
        )
    return results


_EVALUATORS = {
    "earnings_today": evaluate_earnings_today,
    "earnings_next_week": evaluate_earnings_next_week,
    "earnings_tomorrow": evaluate_earnings_tomorrow,
    "popular_weekday": evaluate_popular_weekday,
    "popular_friday": evaluate_popular_friday,
    "thursday_shakeout": evaluate_thursday_shakeout,
    "eod_reversal": evaluate_eod_reversal,
    "gap_fill_trade": evaluate_gap_fill_trade,
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
