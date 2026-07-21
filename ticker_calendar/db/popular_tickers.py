from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ticker_calendar.config.defaults import DEFAULT_POPULAR_TICKERS
from ticker_calendar.db.connection import connect, fetch_by_id
from ticker_calendar.utils import normalize_ticker


@dataclass
class PopularTicker:
    id: int
    ticker: str
    added_at: str


def create_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS popular_tickers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL UNIQUE,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def seed_defaults() -> None:
    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM popular_tickers").fetchone()["c"]
        if count > 0:
            return
        for ticker in DEFAULT_POPULAR_TICKERS:
            try:
                conn.execute(
                    "INSERT INTO popular_tickers (ticker) VALUES (?)",
                    (normalize_ticker(ticker),),
                )
            except Exception:
                pass


def list_all() -> list[PopularTicker]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM popular_tickers ORDER BY ticker"
        ).fetchall()
    return [
        PopularTicker(id=row["id"], ticker=row["ticker"], added_at=row["added_at"])
        for row in rows
    ]


def get_symbols() -> list[str]:
    return [item.ticker for item in list_all()]


def add(ticker: str) -> PopularTicker | None:
    ticker = normalize_ticker(ticker)
    if not ticker:
        return None
    with connect() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO popular_tickers (ticker) VALUES (?)",
                (ticker,),
            )
        except Exception:
            return None
        row = fetch_by_id(conn, "popular_tickers", cursor.lastrowid)
    return PopularTicker(id=row["id"], ticker=row["ticker"], added_at=row["added_at"]) if row else None


def remove(ticker: str) -> bool:
    ticker = normalize_ticker(ticker)
    with connect() as conn:
        cursor = conn.execute(
            "DELETE FROM popular_tickers WHERE ticker = ?", (ticker,)
        )
    return cursor.rowcount > 0


def remove_by_id(ticker_id: int) -> bool:
    with connect() as conn:
        cursor = conn.execute(
            "DELETE FROM popular_tickers WHERE id = ?", (ticker_id,)
        )
    return cursor.rowcount > 0
