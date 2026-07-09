from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from ticker_calendar.rules.evaluator import AlertCandidate
from ticker_calendar.server.job_runner import run_scheduled_check


@patch("ticker_calendar.server.job_runner.send_ntfy", return_value=True)
@patch("ticker_calendar.server.job_runner.alerts_db.record")
@patch("ticker_calendar.server.job_runner.evaluate_rule")
@patch("ticker_calendar.server.job_runner.job_runs.finish_run")
@patch("ticker_calendar.server.job_runner.job_runs.start_run", return_value=1)
@patch("ticker_calendar.server.job_runner.write_heartbeat")
@patch("ticker_calendar.server.job_runner.job_lock")
def test_run_scheduled_check_sends_ntfy(
    mock_lock,
    _heartbeat,
    _start,
    mock_finish,
    mock_evaluate,
    mock_record,
    mock_ntfy,
):
    mock_lock.return_value.__enter__ = MagicMock(return_value=None)
    mock_lock.return_value.__exit__ = MagicMock(return_value=False)

    candidate = AlertCandidate(
        rule_id="popular_weekday",
        rule_name="Popular Stocks Weekday Dip",
        ticker="MSFT",
        message="There is a chance to buy call for MSFT",
        alert_date=date(2026, 7, 8),
    )
    mock_evaluate.return_value = [candidate]
    mock_record.return_value = MagicMock()

    run_scheduled_check("popular_weekday", "10:30")

    mock_evaluate.assert_called_once_with("popular_weekday")
    mock_ntfy.assert_called_once()
    mock_finish.assert_called_once_with(1, status="ok", alerts_fired=1)


@patch("ticker_calendar.server.job_runner.evaluate_rule")
@patch("ticker_calendar.server.job_runner.job_runs.finish_run")
@patch("ticker_calendar.server.job_runner.job_runs.start_run", return_value=2)
@patch("ticker_calendar.server.job_runner.write_heartbeat")
@patch("ticker_calendar.server.job_runner.job_lock")
def test_run_scheduled_check_skips_on_lock_timeout(
    mock_lock,
    _heartbeat,
    _start,
    mock_finish,
    mock_evaluate,
):
    from filelock import Timeout

    mock_lock.return_value.__enter__.side_effect = Timeout("lock")

    run_scheduled_check("earnings_today", "10:00")

    mock_evaluate.assert_not_called()
    mock_finish.assert_called_once()
    assert mock_finish.call_args.kwargs["status"] == "skipped"
