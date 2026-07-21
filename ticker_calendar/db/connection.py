from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "ticker_calendar.db"


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Open a SQLite connection, commit on success, roll back on error, always close.

    Using this as a context manager (``with connect() as conn:``) guarantees the
    connection is closed even when a query raises, avoiding leaked file handles,
    and surfaces database errors to the caller instead of leaving them implicit.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_by_id(conn: sqlite3.Connection, table: str, row_id: int) -> sqlite3.Row | None:
    """Return the row with the given primary-key id from ``table`` (or None)."""
    return conn.execute(
        f"SELECT * FROM {table} WHERE id = ?", (row_id,)
    ).fetchone()


def init_db() -> None:
    from ticker_calendar.db import tickers, popular_tickers, alerts, job_runs

    with connect() as conn:
        tickers.create_table(conn)
        popular_tickers.create_table(conn)
        alerts.create_table(conn)
        job_runs.create_table(conn)
    popular_tickers.seed_defaults()
