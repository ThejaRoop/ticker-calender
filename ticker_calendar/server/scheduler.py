from __future__ import annotations

import logging
import signal
import sys
from functools import partial

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from ticker_calendar.config.alert_rules import MARKET_TIMEZONE, MISFIRE_GRACE_SECONDS, SCHEDULED_CHECKS
from ticker_calendar.server.heartbeat import write_heartbeat
from ticker_calendar.server.job_runner import run_scheduled_check
from ticker_calendar.server.retention import prune_retention

logger = logging.getLogger(__name__)

_WEEKDAY_MAP = {
    "mon": "mon",
    "tue": "tue",
    "wed": "wed",
    "thu": "thu",
    "fri": "fri",
    "sat": "sat",
    "sun": "sun",
}


def parse_weekdays(value: str) -> str:
    """Convert 'mon,tue,wed' to APScheduler day_of_week format."""
    days = []
    for part in value.split(","):
        key = part.strip().lower()
        if key not in _WEEKDAY_MAP:
            raise ValueError(f"Invalid weekday: {part!r}")
        days.append(_WEEKDAY_MAP[key])
    return ",".join(days)


def build_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone=MARKET_TIMEZONE)

    for check in SCHEDULED_CHECKS:
        rule_id = check["rule_id"]
        weekdays = parse_weekdays(check["weekdays"])

        for time_str in check["times"]:
            hour_str, minute_str = time_str.split(":")
            job_id = f"{rule_id}_{time_str.replace(':', '')}"

            scheduler.add_job(
                partial(run_scheduled_check, rule_id, time_str),
                CronTrigger(
                    day_of_week=weekdays,
                    hour=int(hour_str),
                    minute=int(minute_str),
                    timezone=MARKET_TIMEZONE,
                ),
                id=job_id,
                name=f"{rule_id} @ {time_str} ET",
                misfire_grace_time=MISFIRE_GRACE_SECONDS,
                coalesce=True,
                max_instances=1,
                replace_existing=True,
            )

    scheduler.add_job(
        write_heartbeat,
        "interval",
        minutes=1,
        id="heartbeat",
        name="heartbeat",
        replace_existing=True,
    )

    scheduler.add_job(
        prune_retention,
        "interval",
        days=1,
        id="retention",
        name="retention-prune",
        replace_existing=True,
    )

    return scheduler


def list_scheduled_jobs() -> list[dict]:
    """Return configured jobs (for tests and CLI inspection)."""
    jobs = []
    for check in SCHEDULED_CHECKS:
        for time_str in check["times"]:
            jobs.append(
                {
                    "rule_id": check["rule_id"],
                    "time": time_str,
                    "weekdays": check["weekdays"],
                }
            )
    return jobs


def run_server() -> None:
    scheduler = build_scheduler()
    job_count = len([j for j in scheduler.get_jobs() if j.id != "heartbeat"])
    logger.info("Starting alert scheduler (%s rule checks, timezone=%s)", job_count, MARKET_TIMEZONE)
    write_heartbeat("starting")

    def shutdown(signum, _frame):
        logger.info("Received signal %s — shutting down scheduler", signum)
        scheduler.shutdown(wait=False)
        write_heartbeat("stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        write_heartbeat("stopped")
        logger.info("Scheduler stopped")
