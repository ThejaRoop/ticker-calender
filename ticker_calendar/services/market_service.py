from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from ticker_calendar.utils import normalize_ticker

logger = logging.getLogger(__name__)


@dataclass
class Quote:
    ticker: str
    open_price: float | None
    current_price: float | None
    bar_time: str | None = None
    previous_close_price: float | None = None
    day_low_price: float | None = None
    opening_range_high: float | None = None

    @property
    def is_down(self) -> bool:
        if self.open_price is None or self.current_price is None:
            return False
        return self.current_price < self.open_price

    @property
    def change(self) -> float | None:
        if self.open_price is None or self.current_price is None:
            return None
        return self.current_price - self.open_price


def fetch_minute_ohlcv(symbol: str) -> pd.DataFrame:
    """Fetch recent 1-minute OHLCV bars via yfinance (called only at scheduled check times)."""
    ticker = yf.Ticker(normalize_ticker(symbol))
    df = ticker.history(period="2d", interval="1m", prepost=False)
    if df is None or df.empty:
        return pd.DataFrame()
    return df


def quote_from_ohlcv(symbol: str, df: pd.DataFrame) -> Quote:
    """Derive day-open vs latest-minute close from 1m bars."""
    symbol = normalize_ticker(symbol)
    if df is None or df.empty:
        return Quote(ticker=symbol, open_price=None, current_price=None)

    frame = df.copy()
    if hasattr(frame.index, "tz") and frame.index.tz is not None:
        frame.index = frame.index.tz_convert("America/New_York")

    # Previous close is derived from the full multi-day window.
    previous_close_price = None
    try:
        daily_closes = frame.groupby(frame.index.normalize())["Close"].last()
        if len(daily_closes) >= 2:
            previous_close_price = float(daily_closes.iloc[-2])
    except (KeyError, ValueError, TypeError) as exc:
        logger.warning("Could not derive previous close for %s: %s", symbol, exc)
        previous_close_price = None

    # Intraday metrics (open, current, low, opening range) must come from the
    # latest trading day only; the window may span more than one session.
    try:
        latest_day = frame.index.normalize().max()
        today_frame = frame[frame.index.normalize() == latest_day]
    except Exception:
        today_frame = frame

    opens = today_frame["Open"].dropna()
    closes = today_frame["Close"].dropna()
    if opens.empty or closes.empty:
        return Quote(
            ticker=symbol,
            open_price=None,
            current_price=None,
            previous_close_price=previous_close_price,
        )

    day_open = float(opens.iloc[0])
    current = float(closes.iloc[-1])
    bar_time = str(closes.index[-1])

    day_low_price = None
    opening_range_high = None
    if "Low" in today_frame.columns and not today_frame["Low"].dropna().empty:
        day_low_price = float(today_frame["Low"].dropna().min())
    if "High" in today_frame.columns and len(today_frame) >= 15:
        opening_range_high = float(today_frame["High"].iloc[:15].max())

    return Quote(
        ticker=symbol,
        open_price=day_open,
        current_price=current,
        bar_time=bar_time,
        previous_close_price=previous_close_price,
        day_low_price=day_low_price,
        opening_range_high=opening_range_high,
    )


def get_quote(symbol: str) -> Quote:
    symbol = normalize_ticker(symbol)
    return get_quotes([symbol]).get(symbol, Quote(symbol, None, None))


def get_quotes(symbols: list[str]) -> dict[str, Quote]:
    """Batch-fetch minute OHLCV and build quotes. One yfinance call per symbol at job time."""
    tickers = [normalize_ticker(s) for s in symbols if s.strip()]
    result: dict[str, Quote] = {}

    for symbol in tickers:
        try:
            df = fetch_minute_ohlcv(symbol)
            result[symbol] = quote_from_ohlcv(symbol, df)
        except Exception:
            logger.exception("Failed to fetch quote for %s; returning empty quote", symbol)
            result[symbol] = Quote(ticker=symbol, open_price=None, current_price=None)

    return result
