import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "ticker_calendar", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_module_entrypoint_supports_doctor() -> None:
    result = run_cli("doctor")

    assert result.returncode == 0, result.stderr
    assert "Ticker Calendar install verification" in result.stdout
    assert "All checks passed" in result.stdout


def test_module_entrypoint_supports_listing_jobs() -> None:
    result = run_cli("list")

    assert result.returncode == 0, result.stderr
    assert "Scheduled alert checks" in result.stdout
    assert "earnings_today" in result.stdout
