"""
Fetches live WTI and Brent prices from Yahoo Finance.
"""

import yfinance as yf


def get_latest_price(symbol: str) -> float:
    """
    Retrieve the most recent closing price for a given market symbol.

    Args:
        symbol (str): Yahoo Finance symbol.

    Returns:
        float: Latest available price.

    Raises:
        ValueError: If no market data is returned.
    """
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="1d", interval="1m")

    if history.empty:
        raise ValueError(f"No data returned for symbol: {symbol}")

    latest_close = history.iloc[-1]["Close"]
    return float(latest_close)


def get_wti_brent_prices(wti_symbol: str, brent_symbol: str) -> tuple[float, float]:
    """
    Fetch latest WTI and Brent prices.

    Args:
        wti_symbol (str): Yahoo Finance WTI symbol.
        brent_symbol (str): Yahoo Finance Brent symbol.

    Returns:
        tuple[float, float]: (WTI price, Brent price)
    """
    wti_price = get_latest_price(wti_symbol)
    brent_price = get_latest_price(brent_symbol)

    return wti_price, brent_price