import pytest
from filelock import Timeout

from ticker_calendar.server import lock


@pytest.fixture
def lock_path(tmp_path, monkeypatch):
    path = tmp_path / "locks" / "alert_job.lock"
    monkeypatch.setattr(lock, "LOCK_PATH", path)
    return path


def test_job_lock_acquires_and_releases(lock_path):
    with lock.job_lock():
        assert lock_path.parent.exists()
    # Lock is released on exit, so it can be acquired again.
    with lock.job_lock():
        pass


def test_job_lock_raises_on_timeout(lock_path, monkeypatch):
    class FakeLock:
        def __init__(self, *args, **kwargs):
            pass

        def acquire(self):
            raise Timeout("busy")

        def release(self):  # pragma: no cover - not reached when acquire fails
            raise AssertionError("release should not be called when acquire fails")

    monkeypatch.setattr(lock, "FileLock", FakeLock)

    with pytest.raises(Timeout):
        with lock.job_lock(timeout=0.1):
            pass
