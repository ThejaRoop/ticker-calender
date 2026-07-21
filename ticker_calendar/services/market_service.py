from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import yfinance as yf

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
    ticker = yf.Ticker(symbol.strip().upper())
    df = ticker.history(period="2d", interval="1m", prepost=False)
    if df is None or df.empty:
        return pd.DataFrame()
    return df


def quote_from_ohlcv(symbol: str, df: pd.DataFrame) -> Quote:
    """Derive day-open vs latest-minute close from 1m bars."""
    symbol = symbol.strip().upper()
    if df is None or df.empty:
        return Quote(ticker=symbol, open_price=None, current_price=None)

    frame = df.copy()
    if hasattr(frame.index, "tz") and frame.index.tz is not None:
        frame.index = frame.index.tz_convert("America/New_York")

    opens = frame["Open"].dropna()
    closes = frame["Close"].dropna()
    if opens.empty or closes.empty:
        return Quote(ticker=symbol, open_price=None, current_price=None)

    day_open = float(opens.iloc[0])
    current = float(closes.iloc[-1])
    bar_time = str(closes.index[-1])

    previous_close_price = None
    try:
        daily_closes = frame.groupby(frame.index.normalize())["Close"].last()
        if len(daily_closes) >= 2:
            previous_close_price = float(daily_closes.iloc[-2])
    except (KeyError, ValueError, TypeError) as exc:
        logger.warning("Could not derive previous close for %s: %s", symbol, exc)
        previous_close_price = None

    day_low_price = None
    opening_range_high = None
    if "Low" in frame.columns and not frame["Low"].dropna().empty:
        day_low_price = float(frame["Low"].dropna().min())
    if "High" in frame.columns and len(frame) >= 15:
        opening_range_high = float(frame["High"].iloc[:15].max())

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
    return get_quotes([symbol]).get(symbol.upper(), Quote(symbol.upper(), None, None))


def get_quotes(symbols: list[str]) -> dict[str, Quote]:
    """Batch-fetch minute OHLCV and build quotes. One yfinance call per symbol at job time."""
    tickers = [s.strip().upper() for s in symbols if s.strip()]
    result: dict[str, Quote] = {}

    for symbol in tickers:
        try:
            df = fetch_minute_ohlcv(symbol)
            result[symbol] = quote_from_ohlcv(symbol, df)
        except Exception:
            logger.exception("Failed to fetch quote for %s; returning empty quote", symbol)
            result[symbol] = Quote(ticker=symbol, open_price=None, current_price=None)

    return result
