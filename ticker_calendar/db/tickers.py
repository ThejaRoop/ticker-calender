from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date

from ticker_calendar.config.settings import CALENDAR_END, CALENDAR_START
from ticker_calendar.db.connection import connect


@dataclass
class TickerEntry:
    id: int
    ticker: str
    entry_date: date
    source_date: date


def create_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ticker_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            entry_date TEXT NOT NULL,
            source_date TEXT NOT NULL,
            UNIQUE(ticker, entry_date)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_entry_date ON ticker_entries(entry_date)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_source_date ON ticker_entries(source_date)"
    )


def _row_to_entry(row) -> TickerEntry:
    return TickerEntry(
        id=row["id"],
        ticker=row["ticker"],
        entry_date=date.fromisoformat(row["entry_date"]),
        source_date=date.fromisoformat(row["source_date"]),
    )


def get_entries_for_date(entry_date: date) -> list[TickerEntry]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM ticker_entries WHERE entry_date = ? ORDER BY ticker",
            (entry_date.isoformat(),),
        ).fetchall()
    return [_row_to_entry(row) for row in rows]


def get_entries_for_month(year: int, month: int) -> dict[date, list[TickerEntry]]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM ticker_entries
            WHERE entry_date >= ? AND entry_date < ?
            ORDER BY entry_date, ticker
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()

    result: dict[date, list[TickerEntry]] = {}
    for row in rows:
        entry = _row_to_entry(row)
        result.setdefault(entry.entry_date, []).append(entry)
    return result


def get_source_earnings_on(entry_date: date) -> list[str]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT ticker FROM ticker_entries
            WHERE entry_date = ? AND source_date = ?
            ORDER BY ticker
            """,
            (entry_date.isoformat(), entry_date.isoformat()),
        ).fetchall()
    return [row["ticker"] for row in rows]


def get_source_earnings_between(start: date, end: date) -> list[tuple[str, date]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT ticker, entry_date FROM ticker_entries
            WHERE entry_date >= ? AND entry_date <= ?
              AND entry_date = source_date
            ORDER BY entry_date, ticker
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    return [(row["ticker"], date.fromisoformat(row["entry_date"])) for row in rows]


def add_ticker(ticker: str, entry_date: date, source_date: date) -> TickerEntry | None:
    ticker = ticker.strip().upper()
    if not ticker:
        return None
    if entry_date < CALENDAR_START or entry_date > CALENDAR_END:
        return None

    with connect() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO ticker_entries (ticker, entry_date, source_date)
                VALUES (?, ?, ?)
                """,
                (ticker, entry_date.isoformat(), source_date.isoformat()),
            )
        except sqlite3.IntegrityError:
            return None
        row = conn.execute(
            "SELECT * FROM ticker_entries WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return _row_to_entry(row) if row else None


def update_ticker(entry_id: int, new_ticker: str) -> TickerEntry | None:
    new_ticker = new_ticker.strip().upper()
    if not new_ticker:
        return None

    with connect() as conn:
        entry = conn.execute(
            "SELECT * FROM ticker_entries WHERE id = ?", (entry_id,)
        ).fetchone()
        if not entry:
            return None

        try:
            conn.execute(
                "UPDATE ticker_entries SET ticker = ? WHERE id = ?",
                (new_ticker, entry_id),
            )
        except sqlite3.IntegrityError:
            return None

        row = conn.execute(
            "SELECT * FROM ticker_entries WHERE id = ?", (entry_id,)
        ).fetchone()
    return _row_to_entry(row) if row else None


def delete_ticker(entry_id: int) -> bool:
    with connect() as conn:
        cursor = conn.execute(
            "DELETE FROM ticker_entries WHERE id = ?", (entry_id,)
        )
    return cursor.rowcount > 0


def delete_ticker_series(source_date: date, ticker: str) -> int:
    ticker = ticker.strip().upper()
    with connect() as conn:
        cursor = conn.execute(
            """
            DELETE FROM ticker_entries
            WHERE source_date = ? AND ticker = ?
            """,
            (source_date.isoformat(), ticker),
        )
    return cursor.rowcount


def get_entry(entry_id: int) -> TickerEntry | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM ticker_entries WHERE id = ?", (entry_id,)
        ).fetchone()
    return _row_to_entry(row) if row else None
