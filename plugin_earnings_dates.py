from __future__ import annotations

import datetime
import traceback

import yfinance as yf

from ticker_calendar.config.defaults import DEFAULT_POPULAR_TICKERS
from ticker_calendar.config.optional_tickers import OPTIONAL_TICKERS
from ticker_calendar.config.settings import TODAY, CALENDAR_END
from ticker_calendar.db import tickers


def fetch_earnings_dates(symbol):
    ticker = yf.Ticker(symbol)
    try:
        ed = ticker.earnings_dates
    except ImportError as exc:
        print('Earnings date fetch failed because a parser dependency is missing:')
        print(exc)
        print('Install lxml and retry: pip install lxml')
        return None
    except Exception as exc:
        print(f'Earnings date fetch failed for {symbol}:')
        traceback.print_exc()
        return None

    if ed is None or ed.empty:
        return []

    dates = []
    for ts in ed.index:
        if ts is None:
            continue
        try:
            date_value = ts.date()
        except AttributeError:
            try:
                date_value = datetime.date.fromisoformat(str(ts))
            except Exception:
                continue
        if date_value < TODAY or date_value > CALENDAR_END:
            continue
        dates.append(date_value)

    return sorted(set(dates))


def insert_earnings_dates(symbol, earnings_dates):
    inserted = 0
    skipped = 0
    for entry_date in earnings_dates:
        if tickers.add_ticker(symbol, entry_date, entry_date):
            inserted += 1
        else:
            skipped += 1
    return inserted, skipped


def get_sync_symbols():
    symbols: list[str] = []
    for symbol in DEFAULT_POPULAR_TICKERS + OPTIONAL_TICKERS:
        if not symbol:
            continue
        normalized = symbol.strip().upper()
        if normalized and normalized not in symbols:
            symbols.append(normalized)
    return symbols


def sync_default_earnings():
    symbols = get_sync_symbols()
    results = []
    print(f'Syncing upcoming earnings dates for {len(symbols)} symbols...')

    for symbol in symbols:
        dates = fetch_earnings_dates(symbol)
        if not dates:
            print(f'No upcoming earnings dates found for {symbol}.')
            continue

        inserted, skipped = insert_earnings_dates(symbol, dates)
        results.append((symbol, len(dates), inserted, skipped))
        print(
            f'{symbol}: found {len(dates)} upcoming earnings date(s), '
            f'inserted {inserted}, skipped {skipped}.'
        )

    return results


if __name__ == '__main__':
    print('Syncing upcoming earnings dates for default tickers...')
    sync_default_earnings()
    print('Done.')
