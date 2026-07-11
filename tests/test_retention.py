from datetime import datetime, timedelta
from pathlib import Path
import os
import importlib

import ticker_calendar.db.connection as connection
import ticker_calendar.config.server as server_config


def test_prune_retention_removes_old_rows_and_logs(tmp_path, monkeypatch):
    db_path = tmp_path / "ticker_calendar.db"
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(connection, "DB_PATH", db_path)
    monkeypatch.setattr(server_config, "LOG_DIR", log_dir)

    import ticker_calendar.server.retention as retention

    importlib.reload(retention)
    connection.init_db()

    cutoff = datetime.now() - timedelta(days=4)
    old_alert_ts = cutoff.replace(microsecond=0).isoformat(" ")
    old_job_ts = cutoff.replace(microsecond=0).isoformat(" ")

    with connection.connect() as conn:
        conn.execute(
            "INSERT INTO fired_alerts (rule_id, ticker, alert_date, message, created_at) VALUES (?, ?, ?, ?, ?)",
            ("earnings_today", "AAPL", "2026-07-09", "old", old_alert_ts),
        )
        conn.execute(
            "INSERT INTO job_runs (rule_id, scheduled_time, started_at, finished_at, status, alerts_fired, error) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("earnings_today", "10:00", old_job_ts, old_job_ts, "finished", 0, None),
        )

    old_log = log_dir / "old.log"
    old_log.write_text("old", encoding="utf-8")
    old_mtime = (datetime.now() - timedelta(days=4)).timestamp()
    os.utime(old_log, (old_mtime, old_mtime))

    fresh_log = log_dir / "fresh.log"
    fresh_log.write_text("fresh", encoding="utf-8")

    summary = retention.prune_retention(retention_days=3)

    assert summary["alerts_deleted"] == 1
    assert summary["job_runs_deleted"] == 1
    assert not old_log.exists()
    assert fresh_log.exists()
