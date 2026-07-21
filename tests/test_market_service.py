from unittest.mock import MagicMock, patch

import pandas as pd

from ticker_calendar.services.market_service import Quote, quote_from_ohlcv


def test_quote_from_ohlcv_down_from_open():
    index = pd.date_range("2026-07-08 09:30", periods=3, freq="1min", tz="America/New_York")
    df = pd.DataFrame(
        {
            "Open": [100.0, 100.0, 100.0],
            "High": [101.0, 101.0, 100.5],
            "Low": [99.5, 99.0, 98.5],
            "Close": [100.5, 99.5, 98.0],
            "Volume": [1000, 1000, 1000],
        },
        index=index,
    )
    quote = quote_from_ohlcv("MSFT", df)
    assert quote.open_price == 100.0
    assert quote.current_price == 98.0
    assert quote.is_down is True


@patch("ticker_calendar.services.market_service.yf")
def test_fetch_minute_ohlcv_called_at_job_time(mock_yf):
    from ticker_calendar.services.market_service import fetch_minute_ohlcv

    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.history.return_value = pd.DataFrame()

    fetch_minute_ohlcv("MSFT")

    mock_yf.Ticker.assert_called_once_with("MSFT")
    mock_ticker.history.assert_called_once_with(period="2d", interval="1m", prepost=False)
