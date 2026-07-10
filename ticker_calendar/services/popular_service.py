from __future__ import annotations

from dataclasses import dataclass

from ticker_calendar.db import popular_tickers


def list_popular() -> list[popular_tickers.PopularTicker]:
    return popular_tickers.list_all()


def get_symbols() -> list[str]:
    return popular_tickers.get_symbols()


def add_popular(ticker: str) -> popular_tickers.PopularTicker | None:
    return popular_tickers.add(ticker)


def remove_popular(ticker: str) -> bool:
    return popular_tickers.remove(ticker)


def remove_popular_by_id(ticker_id: int) -> bool:
    return popular_tickers.remove_by_id(ticker_id)
