from unittest.mock import patch

from ticker_calendar.server.doctor import check_yfinance_version


@patch("yfinance.__version__", "1.5.1")
def test_doctor_rejects_yfinance_1x():
    errors = check_yfinance_version()
    assert any("curl_cffi" in err for err in errors)


@patch("yfinance.__version__", "0.2.54")
def test_doctor_accepts_yfinance_02x():
    errors = check_yfinance_version()
    assert errors == []
