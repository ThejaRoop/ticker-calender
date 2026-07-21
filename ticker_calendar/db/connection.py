import os
import sqlite3
from pathlib import Path

DB_PATH = Path(
    os.environ.get(
        "TICKER_CALENDAR_DB",
        Path(__file__).resolve().parent.parent.parent / "ticker_calendar.db",
    )
)


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_by_id(conn: sqlite3.Connection, table: str, row_id: int) -> sqlite3.Row | None:
    """Return the row with the given primary-key id from ``table`` (or None)."""
    return conn.execute(
        f"SELECT * FROM {table} WHERE id = ?", (row_id,)
    ).fetchone()


def init_db() -> None:
    from ticker_calendar.db import tickers, popular_tickers, alerts, job_runs

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        tickers.create_table(conn)
        popular_tickers.create_table(conn)
        alerts.create_table(conn)
        job_runs.create_table(conn)
    popular_tickers.seed_defaults()
