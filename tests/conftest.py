import pytest

import ticker_calendar.db.connection as connection


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point the app at an isolated SQLite file with the full schema initialized."""
    db_path = tmp_path / "ticker_calendar.db"
    monkeypatch.setattr(connection, "DB_PATH", db_path)
    connection.init_db()
    yield db_path
