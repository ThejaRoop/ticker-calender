from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ticker_calendar.db.connection import connect


@dataclass
class JobRun:
    id: int
    rule_id: str
    scheduled_time: str
    started_at: str
    finished_at: str | None
    status: str
    alerts_fired: int
    error: str | None


def create_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS job_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id TEXT NOT NULL,
            scheduled_time TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL,
            alerts_fired INTEGER DEFAULT 0,
            error TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_job_runs_started ON job_runs(started_at)"
    )


def start_run(rule_id: str, scheduled_time: str) -> int:
    started_at = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO job_runs (rule_id, scheduled_time, started_at, status)
            VALUES (?, ?, ?, 'running')
            """,
            (rule_id, scheduled_time, started_at),
        )
        return cursor.lastrowid


def finish_run(
    run_id: int,
    *,
    status: str,
    alerts_fired: int = 0,
    error: str | None = None,
) -> None:
    finished_at = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute(
            """
            UPDATE job_runs
            SET finished_at = ?, status = ?, alerts_fired = ?, error = ?
            WHERE id = ?
            """,
            (finished_at, status, alerts_fired, error, run_id),
        )


def list_recent(limit: int = 50) -> list[JobRun]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM job_runs ORDER BY started_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        JobRun(
            id=row["id"],
            rule_id=row["rule_id"],
            scheduled_time=row["scheduled_time"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            status=row["status"],
            alerts_fired=row["alerts_fired"],
            error=row["error"],
        )
        for row in rows
    ]
