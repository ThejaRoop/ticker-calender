#!/usr/bin/env python3
"""Thin wrapper — use: python run_server.py doctor"""

from ticker_calendar.server.doctor import run_doctor

if __name__ == "__main__":
    raise SystemExit(run_doctor())
