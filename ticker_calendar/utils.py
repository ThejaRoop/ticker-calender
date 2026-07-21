"""Small shared helpers used across the package."""

from __future__ import annotations

from datetime import datetime


def normalize_ticker(value: str) -> str:
    """Canonical ticker form: trimmed and upper-cased."""
    return value.strip().upper()


def now_iso(timespec: str = "seconds") -> str:
    """Current local time as an ISO-8601 string (seconds precision by default)."""
    return datetime.now().isoformat(timespec=timespec)
