"""
Fetches live WTI and Brent prices from Yahoo Finance.
"""

import yfinance as yf

from config import (
    PRICE_INTERVAL,
    PRICE_PERIOD,
    FALLBACK_PRICE_INTERVAL,
    FALLBACK_PRICE_PERIOD,
    LAST_RESORT_PRICE_INTERVAL,
    LAST_RESORT_PRICE_PERIOD,
)


def fetch_price_history(symbol: str, period: str, interval: str):
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period, interval=interval)


def get_latest_price(symbol: str) -> float:
    """
    Retrieve the latest available price for a symbol using fallback intervals.
    """
    attempts = [
        (PRICE_PERIOD, PRICE_INTERVAL),
        (FALLBACK_PRICE_PERIOD, FALLBACK_PRICE_INTERVAL),
        (LAST_RESORT_PRICE_PERIOD, LAST_RESORT_PRICE_INTERVAL),
    ]

    for period, interval in attempts:
        history = fetch_price_history(symbol, period, interval)

        if not history.empty:
            latest_close = history.iloc[-1]["Close"]
            return float(latest_close)

    raise ValueError(f"No data returned for symbol after all fallbacks: {symbol}")


def get_wti_brent_prices(wti_symbol: str, brent_symbol: str) -> tuple[float, float]:
    wti_price = get_latest_price(wti_symbol)
    brent_price = get_latest_price(brent_symbol)
    return wti_price, brent_price