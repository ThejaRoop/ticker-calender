from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from ticker_calendar.config.server import LOG_DIR
from ticker_calendar.db.connection import connect

logger = logging.getLogger(__name__)


def prune_retention(retention_days: int = 3) -> dict[str, int]:
    """Delete old alert/job history rows and old log files beyond the retention window."""
    # Timestamps are stored in different clocks/formats:
    #   fired_alerts.created_at -> SQLite CURRENT_TIMESTAMP: UTC, "YYYY-MM-DD HH:MM:SS"
    #   job_runs.started_at     -> datetime.now().isoformat(): local, "YYYY-MM-DDTHH:MM:SS"
    # Each cutoff must match its column's clock and format for string comparison.
    utc_cutoff = datetime.utcnow() - timedelta(days=retention_days)
    local_cutoff = datetime.now() - timedelta(days=retention_days)
    alerts_cutoff_text = utc_cutoff.replace(microsecond=0).isoformat(" ")
    job_runs_cutoff_text = local_cutoff.isoformat(timespec="seconds")

    alerts_deleted = 0
    job_runs_deleted = 0
    logs_deleted = 0

    with connect() as conn:
        alerts_deleted = conn.execute(
            "DELETE FROM fired_alerts WHERE created_at < ?",
            (alerts_cutoff_text,),
        ).rowcount
        job_runs_deleted = conn.execute(
            "DELETE FROM job_runs WHERE started_at < ?",
            (job_runs_cutoff_text,),
        ).rowcount

    if LOG_DIR.exists():
        for path in LOG_DIR.iterdir():
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".log", ".txt"}:
                continue
            try:
                if datetime.fromtimestamp(path.stat().st_mtime) < local_cutoff:
                    path.unlink()
                    logs_deleted += 1
            except OSError as exc:
                logger.warning("Could not prune log file %s: %s", path, exc)
                continue

    logger.info(
        "Pruned retention older than %s days: alerts=%s job_runs=%s logs=%s",
        retention_days,
        alerts_deleted,
        job_runs_deleted,
        logs_deleted,
    )
    return {
        "alerts_deleted": alerts_deleted,
        "job_runs_deleted": job_runs_deleted,
        "logs_deleted": logs_deleted,
    }
