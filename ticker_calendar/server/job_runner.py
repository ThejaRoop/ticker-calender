import logging

from filelock import Timeout

from ticker_calendar.db import alerts as alerts_db
from ticker_calendar.db import job_runs
from ticker_calendar.rules.evaluator import evaluate_rule
from ticker_calendar.server.heartbeat import write_heartbeat
from ticker_calendar.server.lock import job_lock
from ticker_calendar.services.notification_service import format_alert_message, send_ntfy

logger = logging.getLogger(__name__)


def run_scheduled_check(rule_id: str, scheduled_time: str) -> None:
    """Evaluate one rule at its scheduled fire time, notify, and log the run."""
    run_id = job_runs.start_run(rule_id, scheduled_time)
    logger.info("Starting scheduled check rule=%s time=%s run_id=%s", rule_id, scheduled_time, run_id)

    try:
        with job_lock():
            candidates = evaluate_rule(rule_id)
            fired = 0

            for candidate in candidates:
                record = alerts_db.record(
                    candidate.rule_id,
                    candidate.ticker,
                    candidate.alert_date,
                    candidate.message,
                )
                if not record:
                    continue

                fired += 1
                message = format_alert_message(candidate)
                if send_ntfy(message, title=f"Buy Call: {candidate.ticker}"):
                    logger.info("Alert sent: %s (%s)", candidate.ticker, candidate.rule_id)
                else:
                    logger.error("Failed to send ntfy for %s", candidate.ticker)

            job_runs.finish_run(run_id, status="ok", alerts_fired=fired)
            write_heartbeat(f"ok rule={rule_id} alerts={fired}")
            logger.info(
                "Finished scheduled check rule=%s time=%s alerts_fired=%s",
                rule_id,
                scheduled_time,
                fired,
            )

    except Timeout:
        job_runs.finish_run(
            run_id,
            status="skipped",
            error="Could not acquire job lock (another check still running)",
        )
        logger.warning("Skipped rule=%s time=%s — lock held by another job", rule_id, scheduled_time)

    except Exception as exc:
        job_runs.finish_run(run_id, status="error", error=str(exc))
        write_heartbeat(f"error rule={rule_id}")
        logger.exception("Scheduled check failed rule=%s time=%s", rule_id, scheduled_time)
