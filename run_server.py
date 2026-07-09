#!/usr/bin/env python3
"""Run the alert scheduler on Ubuntu (systemd) or locally for testing."""

from __future__ import annotations

import argparse
import logging
import sys

from ticker_calendar.config.server import LOG_DIR
from ticker_calendar.db.connection import init_db
from ticker_calendar.server.job_runner import run_scheduled_check
from ticker_calendar.server.scheduler import list_scheduled_jobs, run_server


def setup_logging(verbose: bool = False) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "server.log"

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


def cmd_list(_args: argparse.Namespace) -> int:
    print("Scheduled alert checks (America/New_York):")
    print("-" * 50)
    for job in list_scheduled_jobs():
        print(f"  {job['rule_id']:20s}  {job['time']}  ({job['weekdays']})")
    return 0


def cmd_run_rule(args: argparse.Namespace) -> int:
    run_scheduled_check(args.rule_id, args.time)
    return 0


def cmd_serve(_args: argparse.Namespace) -> int:
    run_server()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ticker Calendar alert server")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("serve", help="Start the long-running scheduler (use with systemd)")
    sub.add_parser("list", help="Show all scheduled check times")

    run_parser = sub.add_parser("run-rule", help="Run one rule immediately (testing)")
    run_parser.add_argument("rule_id", help="Rule id, e.g. earnings_today")
    run_parser.add_argument("--time", default="manual", help="Label for job_runs log")

    args = parser.parse_args()
    setup_logging(args.verbose)
    init_db()

    if args.command == "list":
        return cmd_list(args)
    if args.command == "run-rule":
        return cmd_run_rule(args)
    if args.command == "serve":
        return cmd_serve(args)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
