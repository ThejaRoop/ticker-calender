import importlib
from datetime import date

import pytest

import ticker_calendar.db.connection as connection


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "ticker_calendar.db"
    monkeypatch.setattr(connection, "DB_PATH", db_path)

    from ticker_calendar.db import alerts, popular_tickers, tickers

    connection.init_db()
    return {
        "alerts": alerts,
        "popular_tickers": popular_tickers,
        "tickers": tickers,
    }


def test_connection_commits_and_persists(temp_db):
    with connection.connect() as conn:
        conn.execute(
            "INSERT INTO popular_tickers (ticker) VALUES (?)", ("ZZZZ",),
        )

    # A brand new connection must see the row -> the write was committed.
    with connection.connect() as conn:
        row = conn.execute(
            "SELECT ticker FROM popular_tickers WHERE ticker = ?", ("ZZZZ",),
        ).fetchone()
    assert row is not None and row["ticker"] == "ZZZZ"


def test_connection_rolls_back_on_error(temp_db):
    with pytest.raises(ValueError):
        with connection.connect() as conn:
            conn.execute(
                "INSERT INTO popular_tickers (ticker) VALUES (?)", ("ROLLBACKME",),
            )
            raise ValueError("boom")

    with connection.connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM popular_tickers WHERE ticker = ?", ("ROLLBACKME",),
        ).fetchone()
    assert row is None


def test_record_dedups_duplicate_alert(temp_db):
    alerts = temp_db["alerts"]
    day = date(2026, 7, 8)

    first = alerts.record("earnings_today", "AAPL", day, "buy call")
    assert first is not None

    # UNIQUE(rule_id, ticker, alert_date) -> duplicate returns None, not an error.
    second = alerts.record("earnings_today", "AAPL", day, "buy call")
    assert second is None


def test_record_propagates_non_integrity_errors(temp_db, monkeypatch):
    alerts = temp_db["alerts"]

    class BrokenDate:
        def isoformat(self):
            raise RuntimeError("db unavailable")

    # A non-integrity failure must NOT be swallowed as a silent dedup.
    with pytest.raises(RuntimeError):
        alerts.record("earnings_today", "AAPL", BrokenDate(), "buy call")


def test_popular_add_dedups(temp_db):
    popular_tickers = temp_db["popular_tickers"]

    created = popular_tickers.add("NEWSYM")
    assert created is not None
    assert popular_tickers.add("NEWSYM") is None
