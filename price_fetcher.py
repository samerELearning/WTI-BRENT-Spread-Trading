"""
Fetches live MT5 quotes, symbol trading metadata, and simple order execution helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import MetaTrader5 as mt5

from config import MT5_TERMINAL_PATH


@dataclass
class SymbolQuote:
    symbol: str
    bid: float
    ask: float
    mid: float
    tick_time: datetime


@dataclass
class SymbolTradingSpecs:
    symbol: str
    volume_min: float
    volume_max: float
    volume_step: float
    trade_contract_size: float
    trade_mode: int
    visible: bool


def initialize_mt5(login: int, password: str, server: str) -> None:
    connected = mt5.initialize(
        path=MT5_TERMINAL_PATH,
        login=login,
        password=password,
        server=server,
    )

    if not connected:
        error = mt5.last_error()
        raise RuntimeError(f"MT5 initialize() failed: {error}")


def shutdown_mt5() -> None:
    mt5.shutdown()


def get_symbol_tick(symbol: str):
    tick = mt5.symbol_info_tick(symbol)

    if tick is None:
        raise ValueError(f"No tick data returned for symbol: {symbol}")

    return tick


def get_symbol_quote(symbol: str) -> SymbolQuote:
    tick = get_symbol_tick(symbol)

    if tick.bid <= 0 or tick.ask <= 0:
        raise ValueError(f"Invalid bid/ask for symbol: {symbol}")

    tick_time = datetime.fromtimestamp(tick.time)
    mid_price = (tick.bid + tick.ask) / 2

    return SymbolQuote(
        symbol=symbol,
        bid=float(tick.bid),
        ask=float(tick.ask),
        mid=float(mid_price),
        tick_time=tick_time,
    )


def get_symbol_trading_specs(symbol: str) -> SymbolTradingSpecs:
    info = mt5.symbol_info(symbol)

    if info is None:
        raise ValueError(f"No symbol info returned for symbol: {symbol}")

    return SymbolTradingSpecs(
        symbol=symbol,
        volume_min=float(info.volume_min),
        volume_max=float(info.volume_max),
        volume_step=float(info.volume_step),
        trade_contract_size=float(info.trade_contract_size),
        trade_mode=int(info.trade_mode),
        visible=bool(info.visible),
    )


def ensure_symbol_selected(symbol: str) -> None:
    info = mt5.symbol_info(symbol)

    if info is None:
        raise ValueError(f"Symbol not found: {symbol}")

    if info.visible:
        return

    selected = mt5.symbol_select(symbol, True)
    if not selected:
        error = mt5.last_error()
        raise RuntimeError(f"Failed to select symbol {symbol}: {error}")


def _get_supported_filling_modes() -> list[int]:
    return [
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_FOK,
        mt5.ORDER_FILLING_RETURN,
    ]


def place_market_buy_order(
    symbol: str,
    volume: float,
    deviation: int = 20,
    magic: int = 20260329,
    comment: str = "python demo buy",
):
    ensure_symbol_selected(symbol)

    tick = get_symbol_tick(symbol)
    price = float(tick.ask)

    if price <= 0:
        raise ValueError(f"Invalid ask price for symbol: {symbol}")

    last_result = None

    for filling_mode in _get_supported_filling_modes():
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "deviation": int(deviation),
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        result = mt5.order_send(request)

        if result is None:
            error = mt5.last_error()
            raise RuntimeError(f"order_send() returned None: {error}")

        last_result = result

        if result.retcode != mt5.TRADE_RETCODE_INVALID_FILL:
            return result

    return last_result


def place_market_sell_order(
    symbol: str,
    volume: float,
    deviation: int = 20,
    magic: int = 20260329,
    comment: str = "python demo sell",
):
    ensure_symbol_selected(symbol)

    tick = get_symbol_tick(symbol)
    price = float(tick.bid)

    if price <= 0:
        raise ValueError(f"Invalid bid price for symbol: {symbol}")

    last_result = None

    for filling_mode in _get_supported_filling_modes():
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": int(deviation),
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        result = mt5.order_send(request)

        if result is None:
            error = mt5.last_error()
            raise RuntimeError(f"order_send() returned None: {error}")

        last_result = result

        if result.retcode != mt5.TRADE_RETCODE_INVALID_FILL:
            return result

    return last_result


def close_buy_position(
    symbol: str,
    position_ticket: int,
    volume: float,
    deviation: int = 20,
    magic: int = 20260329,
    comment: str = "python close buy",
):
    ensure_symbol_selected(symbol)

    tick = get_symbol_tick(symbol)
    price = float(tick.bid)

    if price <= 0:
        raise ValueError(f"Invalid bid price for symbol: {symbol}")

    last_result = None

    for filling_mode in _get_supported_filling_modes():
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_SELL,
            "position": int(position_ticket),
            "price": price,
            "deviation": int(deviation),
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        result = mt5.order_send(request)

        if result is None:
            error = mt5.last_error()
            raise RuntimeError(f"order_send() returned None while closing buy: {error}")

        last_result = result

        if result.retcode != mt5.TRADE_RETCODE_INVALID_FILL:
            return result

    return last_result


def close_sell_position(
    symbol: str,
    position_ticket: int,
    volume: float,
    deviation: int = 20,
    magic: int = 20260329,
    comment: str = "python close sell",
):
    ensure_symbol_selected(symbol)

    tick = get_symbol_tick(symbol)
    price = float(tick.ask)

    if price <= 0:
        raise ValueError(f"Invalid ask price for symbol: {symbol}")

    last_result = None

    for filling_mode in _get_supported_filling_modes():
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY,
            "position": int(position_ticket),
            "price": price,
            "deviation": int(deviation),
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        result = mt5.order_send(request)

        if result is None:
            error = mt5.last_error()
            raise RuntimeError(f"order_send() returned None while closing sell: {error}")

        last_result = result

        if result.retcode != mt5.TRADE_RETCODE_INVALID_FILL:
            return result

    return last_result


def open_short_spread_pair(
    wti_symbol: str,
    brent_symbol: str,
    volume: float,
):
    """
    Open the short spread pair:
    Buy WTI + Sell BRENT

    If the second leg fails, roll back the first leg.
    """
    wti_result = place_market_buy_order(
        symbol=wti_symbol,
        volume=volume,
        comment="spread wti long",
    )

    if wti_result.retcode != mt5.TRADE_RETCODE_DONE:
        return {
            "success": False,
            "stage": "wti_buy_failed",
            "wti_result": wti_result,
            "brent_result": None,
            "rollback_result": None,
        }

    brent_result = place_market_sell_order(
        symbol=brent_symbol,
        volume=volume,
        comment="spread brent short",
    )

    if brent_result.retcode != mt5.TRADE_RETCODE_DONE:
        rollback_result = close_buy_position(
            symbol=wti_symbol,
            position_ticket=wti_result.order,
            volume=wti_result.volume,
            comment="rollback wti long",
        )

        return {
            "success": False,
            "stage": "brent_sell_failed_rolled_back_wti",
            "wti_result": wti_result,
            "brent_result": brent_result,
            "rollback_result": rollback_result,
        }

    return {
        "success": True,
        "stage": "opened_short_spread",
        "wti_result": wti_result,
        "brent_result": brent_result,
        "rollback_result": None,
    }


def close_short_spread_pair(
    wti_symbol: str,
    brent_symbol: str,
    wti_position_ticket: int,
    brent_position_ticket: int,
    volume: float,
):
    """
    Close the short spread pair:
    Close WTI buy + close BRENT sell
    """
    wti_close_result = close_buy_position(
        symbol=wti_symbol,
        position_ticket=wti_position_ticket,
        volume=volume,
        comment="close spread wti long",
    )

    brent_close_result = close_sell_position(
        symbol=brent_symbol,
        position_ticket=brent_position_ticket,
        volume=volume,
        comment="close spread brent short",
    )

    return {
        "success": (
            wti_close_result.retcode == mt5.TRADE_RETCODE_DONE
            and brent_close_result.retcode == mt5.TRADE_RETCODE_DONE
        ),
        "wti_close_result": wti_close_result,
        "brent_close_result": brent_close_result,
    }


def get_wti_brent_quotes(wti_symbol: str, brent_symbol: str) -> tuple[SymbolQuote, SymbolQuote]:
    wti_quote = get_symbol_quote(wti_symbol)
    brent_quote = get_symbol_quote(brent_symbol)
    return wti_quote, brent_quote


def get_latest_price(symbol: str) -> float:
    quote = get_symbol_quote(symbol)
    return quote.mid


def get_wti_brent_prices(wti_symbol: str, brent_symbol: str) -> tuple[float, float]:
    wti_price = get_latest_price(wti_symbol)
    brent_price = get_latest_price(brent_symbol)
    return wti_price, brent_price


def get_executable_short_spread(wti_symbol: str, brent_symbol: str) -> float:
    """
    Short spread executable logic:
    Buy WTI at ASK, Sell BRENT at BID

    Spread = BRENT bid - WTI ask
    """
    wti_quote = get_symbol_quote(wti_symbol)
    brent_quote = get_symbol_quote(brent_symbol)

    return float(brent_quote.bid - wti_quote.ask)