from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from ticker_calendar.config.settings import CALENDAR_END, RECURRENCE_DAYS
from ticker_calendar.db import tickers


def recurrence_dates(source_date: date) -> list[date]:
    dates = [source_date]
    current = source_date
    while True:
        current = current + timedelta(days=RECURRENCE_DAYS)
        if current > CALENDAR_END:
            break
        dates.append(current)
    return dates


def add_ticker_with_recurrence(
    ticker: str, earning_date: date
) -> tuple[list[tickers.TickerEntry], list[date]]:
    added: list[tickers.TickerEntry] = []
    skipped: list[date] = []

    for entry_date in recurrence_dates(earning_date):
        entry = tickers.add_ticker(ticker, entry_date, earning_date)
        if entry:
            added.append(entry)
        else:
            skipped.append(entry_date)

    return added, skipped


def update_ticker(entry_id: int, new_ticker: str) -> tickers.TickerEntry | None:
    return tickers.update_ticker(entry_id, new_ticker)


def delete_ticker(entry_id: int, delete_series: bool = False) -> int:
    entry = tickers.get_entry(entry_id)
    if not entry:
        return 0

    if delete_series and entry.entry_date == entry.source_date:
        return tickers.delete_ticker_series(entry.source_date, entry.ticker)

    return 1 if tickers.delete_ticker(entry_id) else 0


def get_month_data(year: int, month: int) -> dict[date, list[tickers.TickerEntry]]:
    return tickers.get_entries_for_month(year, month)


def get_day_entries(entry_date: date) -> list[tickers.TickerEntry]:
    return tickers.get_entries_for_date(entry_date)
