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
    cutoff = datetime.now() - timedelta(days=retention_days)
    cutoff_text = cutoff.replace(microsecond=0).isoformat(" ")

    alerts_deleted = 0
    job_runs_deleted = 0
    logs_deleted = 0

    with connect() as conn:
        alerts_deleted = conn.execute(
            "DELETE FROM fired_alerts WHERE created_at < ?",
            (cutoff_text,),
        ).rowcount
        job_runs_deleted = conn.execute(
            "DELETE FROM job_runs WHERE started_at < ?",
            (cutoff_text,),
        ).rowcount

    if LOG_DIR.exists():
        for path in LOG_DIR.iterdir():
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".log", ".txt"}:
                continue
            try:
                if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                    path.unlink()
                    logs_deleted += 1
            except OSError:
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
