from dataclasses import dataclass
from datetime import date, datetime

from ticker_calendar.db.connection import connect


@dataclass
class AlertRecord:
    id: int
    rule_id: str
    ticker: str
    alert_date: date
    message: str
    created_at: str


def create_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fired_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            alert_date TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(rule_id, ticker, alert_date)
        )
        """
    )


def _row_to_alert(row) -> AlertRecord:
    return AlertRecord(
        id=row["id"],
        rule_id=row["rule_id"],
        ticker=row["ticker"],
        alert_date=date.fromisoformat(row["alert_date"]),
        message=row["message"],
        created_at=row["created_at"],
    )


def was_fired(rule_id: str, ticker: str, alert_date: date) -> bool:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM fired_alerts
            WHERE rule_id = ? AND ticker = ? AND alert_date = ?
            """,
            (rule_id, ticker.upper(), alert_date.isoformat()),
        ).fetchone()
    return row is not None


def record(rule_id: str, ticker: str, alert_date: date, message: str) -> AlertRecord | None:
    with connect() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO fired_alerts (rule_id, ticker, alert_date, message)
                VALUES (?, ?, ?, ?)
                """,
                (rule_id, ticker.upper(), alert_date.isoformat(), message),
            )
        except Exception:
            return None
        row = conn.execute(
            "SELECT * FROM fired_alerts WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return _row_to_alert(row) if row else None


def list_recent(limit: int = 100) -> list[AlertRecord]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM fired_alerts
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_row_to_alert(row) for row in rows]


def list_for_date(alert_date: date) -> list[AlertRecord]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM fired_alerts
            WHERE alert_date = ?
            ORDER BY created_at DESC
            """,
            (alert_date.isoformat(),),
        ).fetchall()
    return [_row_to_alert(row) for row in rows]
