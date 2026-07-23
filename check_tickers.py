#!/usr/bin/env python3
"""Check all tickers in the database - both popular tickers and earnings calendar entries."""

from __future__ import annotations

from collections import Counter
from datetime import date

from ticker_calendar.db.connection import connect, init_db
from ticker_calendar.db.popular_tickers import get_symbols as get_popular_symbols


def get_all_earnings_tickers() -> list[str]:
    """Get all unique tickers from the earnings calendar."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT ticker FROM ticker_entries ORDER BY ticker"
        ).fetchall()
    return [row["ticker"] for row in rows]


def get_ticker_counts() -> dict[str, int]:
    """Get count of earnings entries per ticker."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT ticker, COUNT(*) as cnt FROM ticker_entries GROUP BY ticker ORDER BY cnt DESC"
        ).fetchall()
    return {row["ticker"]: row["cnt"] for row in rows}


def get_tickers_by_date_range(start: date, end: date) -> list[tuple[str, date]]:
    """Get all tickers with their earnings dates in a date range."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT ticker, entry_date FROM ticker_entries
            WHERE entry_date >= ? AND entry_date <= ?
            ORDER BY entry_date, ticker
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    return [(row["ticker"], date.fromisoformat(row["entry_date"])) for row in rows]


def main():
    init_db()
    
    print("=" * 60)
    print("POPULAR TICKERS (used for weekday/Friday alerts)")
    print("=" * 60)
    popular = get_popular_symbols()
    if popular:
        for ticker in popular:
            print(f"  {ticker}")
    else:
        print("  (none)")
    print(f"\nTotal: {len(popular)} popular tickers\n")
    
    print("=" * 60)
    print("EARNINGS CALENDAR TICKERS (all unique tickers)")
    print("=" * 60)
    earnings_tickers = get_all_earnings_tickers()
    if earnings_tickers:
        for ticker in earnings_tickers:
            print(f"  {ticker}")
    else:
        print("  (none)")
    print(f"\nTotal: {len(earnings_tickers)} unique tickers in calendar\n")
    
    print("=" * 60)
    print("TICKER ENTRY COUNTS (how many dates each ticker has)")
    print("=" * 60)
    counts = get_ticker_counts()
    if counts:
        for ticker, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  {ticker}: {count} date(s)")
    else:
        print("  (none)")
    print()


if __name__ == "__main__":
    main()