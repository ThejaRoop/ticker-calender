"""Preflight checks before running the alert server."""

from __future__ import annotations

import importlib
import sys


def check_python() -> list[str]:
    errors: list[str] = []
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 8):
        errors.append(f"Python 3.8+ required (found {major}.{minor})")
    elif (major, minor) < (3, 10):
        print(
            f"WARNING: Python {major}.{minor} works with pinned yfinance 0.2.54. "
            "Python 3.10+ is recommended for long-term support."
        )
    return errors


def check_imports() -> list[str]:
    errors: list[str] = []
    modules = [
        "yfinance",
        "requests",
        "pandas",
        "apscheduler",
        "filelock",
        "lxml",
        "ticker_calendar.server.scheduler",
        "ticker_calendar.services.market_service",
        "ticker_calendar.services.notification_service",
    ]
    for name in modules:
        try:
            importlib.import_module(name)
        except ImportError as exc:
            errors.append(f"Missing import {name}: {exc}")
    return errors


def check_yfinance_version() -> list[str]:
    errors: list[str] = []
    import yfinance

    version = getattr(yfinance, "__version__", "unknown")
    if version.startswith("1."):
        errors.append(
            f"yfinance {version} requires curl_cffi>=0.15 (Python 3.10+). "
            "Pin yfinance==0.2.54 in requirements.txt."
        )
    else:
        print(f"OK: yfinance {version}")
    return errors


def check_db_and_schedule() -> list[str]:
    errors: list[str] = []
    try:
        from ticker_calendar.db.connection import init_db
        from ticker_calendar.server.scheduler import list_scheduled_jobs

        init_db()
        jobs = list_scheduled_jobs()
        if not jobs:
            errors.append("No scheduled jobs configured in SCHEDULED_CHECKS")
        else:
            print(f"OK: {len(jobs)} scheduled alert checks configured")
    except Exception as exc:
        errors.append(f"DB/schedule check failed: {exc}")
    return errors


def run_doctor() -> int:
    print("Ticker Calendar install verification")
    print("-" * 40)

    all_errors: list[str] = []
    all_errors.extend(check_python())
    all_errors.extend(check_imports())
    all_errors.extend(check_yfinance_version())
    all_errors.extend(check_db_and_schedule())

    if all_errors:
        print("\nFAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("\nAll checks passed. Ready to run: python run_server.py serve")
    return 0
