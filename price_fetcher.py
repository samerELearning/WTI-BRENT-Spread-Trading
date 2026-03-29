"""
Fetches live WTI and Brent prices from MetaTrader 5.
"""

from __future__ import annotations

import MetaTrader5 as mt5


def initialize_mt5(login: int, password: str, server: str) -> None:
    """
    Initialize the MT5 terminal connection directly with account credentials.
    """
    connected = mt5.initialize(
        login=login,
        password=password,
        server=server,
    )

    if not connected:
        error = mt5.last_error()
        raise RuntimeError(f"MT5 initialize() failed: {error}")


def shutdown_mt5() -> None:
    """
    Cleanly close the MT5 connection.
    """
    mt5.shutdown()


def get_symbol_tick(symbol: str):
    """
    Return the full tick object for a symbol.
    """
    tick = mt5.symbol_info_tick(symbol)

    if tick is None:
        raise ValueError(f"No tick data returned for symbol: {symbol}")

    return tick


def get_latest_price(symbol: str) -> float:
    """
    Retrieve the latest marketable display price for a symbol using the mid price.
    Mid price = (bid + ask) / 2
    """
    tick = get_symbol_tick(symbol)

    if tick.bid <= 0 or tick.ask <= 0:
        raise ValueError(f"Invalid bid/ask for symbol: {symbol}")

    mid_price = (tick.bid + tick.ask) / 2
    return float(mid_price)


def get_wti_brent_prices(wti_symbol: str, brent_symbol: str) -> tuple[float, float]:
    """
    Return simple display prices for WTI and Brent.
    """
    wti_price = get_latest_price(wti_symbol)
    brent_price = get_latest_price(brent_symbol)
    return wti_price, brent_price


def get_executable_short_spread(wti_symbol: str, brent_symbol: str) -> float:
    """
    Real executable spread for the short-spread setup:
    Buy WTI at ASK, Sell Brent at BID

    Spread = Brent bid - WTI ask
    """
    wti_tick = get_symbol_tick(wti_symbol)
    brent_tick = get_symbol_tick(brent_symbol)

    return float(brent_tick.bid - wti_tick.ask)