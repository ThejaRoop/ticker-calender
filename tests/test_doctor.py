from unittest.mock import patch

from ticker_calendar.server import doctor
from ticker_calendar.server.doctor import (
    check_db_and_schedule,
    check_imports,
    check_python,
    check_yfinance_version,
    run_doctor,
)


@patch("yfinance.__version__", "1.5.1")
def test_doctor_rejects_yfinance_1x():
    errors = check_yfinance_version()
    assert any("curl_cffi" in err for err in errors)


@patch("yfinance.__version__", "0.2.54")
def test_doctor_accepts_yfinance_02x():
    errors = check_yfinance_version()
    assert errors == []


def test_check_python_accepts_supported_version():
    # The test runner uses a supported interpreter, so there should be no errors.
    assert check_python() == []


def test_check_python_rejects_too_old(monkeypatch):
    monkeypatch.setattr(doctor.sys, "version_info", (3, 7, 0))
    errors = check_python()
    assert any("3.8+" in err for err in errors)


def test_check_imports_all_present():
    assert check_imports() == []


def test_check_imports_reports_missing(monkeypatch):
    real_import = doctor.importlib.import_module

    def fake_import(name):
        if name == "yfinance":
            raise ImportError("boom")
        return real_import(name)

    monkeypatch.setattr(doctor.importlib, "import_module", fake_import)
    errors = check_imports()
    assert any("yfinance" in err for err in errors)


def test_check_db_and_schedule_ok(temp_db):
    assert check_db_and_schedule() == []


def test_check_db_and_schedule_reports_failure(monkeypatch, temp_db):
    import ticker_calendar.server.scheduler as scheduler

    monkeypatch.setattr(scheduler, "list_scheduled_jobs", lambda: [])
    errors = check_db_and_schedule()
    assert any("No scheduled jobs" in err for err in errors)


def test_run_doctor_success(temp_db):
    assert run_doctor() == 0


def test_run_doctor_reports_errors(monkeypatch, temp_db):
    monkeypatch.setattr(doctor.sys, "version_info", (3, 7, 0))
    assert run_doctor() == 1
