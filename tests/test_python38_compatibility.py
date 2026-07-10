from pathlib import Path


def test_future_annotations_are_enabled_for_py38_compatibility():
    modules = [
        Path("ticker_calendar/db/alerts.py"),
        Path("ticker_calendar/db/job_runs.py"),
        Path("ticker_calendar/db/popular_tickers.py"),
        Path("ticker_calendar/db/tickers.py"),
        Path("ticker_calendar/rules/evaluator.py"),
        Path("ticker_calendar/server/lock.py"),
        Path("ticker_calendar/services/alert_service.py"),
        Path("ticker_calendar/services/calendar_service.py"),
        Path("ticker_calendar/services/market_service.py"),
        Path("ticker_calendar/services/notification_service.py"),
        Path("ticker_calendar/ui/ticker_dialog.py"),
        Path("plugin_earnings_dates.py"),
    ]

    for module_path in modules:
        source = module_path.read_text(encoding="utf-8")
        assert "from __future__ import annotations" in source
