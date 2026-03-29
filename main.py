"""
Main runner for the WTI-BRENT MT5 spread monitor.
"""

from __future__ import annotations

import time

from alerts import send_console_alert
from config import (
    BRENT_SYMBOL,
    CHECK_INTERVAL_SECONDS,
    ENABLE_ALERTS,
    ENTRY_SPREAD,
    PAIR_LOT_SIZE,
    WTI_SYMBOL,
)
from price_fetcher import (
    close_short_spread_pair,
    detect_open_spread_state,
    get_executable_short_spread,
    get_position_type_name,
    get_wti_brent_quotes,
    initialize_mt5,
    open_short_spread_pair,
    shutdown_mt5,
)
from spread_engine import calculate_spread, is_entry_signal


def print_order_result(title: str, result) -> None:
    print(title)
    print(f"  retcode: {result.retcode}")
    print(f"  order: {result.order}")
    print(f"  deal: {result.deal}")
    print(f"  volume: {result.volume}")
    print(f"  price: {result.price}")
    print(f"  comment: {result.comment}")
    print(f"  request_id: {result.request_id}")
    print("-" * 100)


def print_position_info(label: str, position) -> None:
    if position is None:
        print(f"  {label}: none")
        return

    print(
        f"  {label}: "
        f"ticket={position.ticket}, "
        f"type={get_position_type_name(position.position_type)}, "
        f"volume={position.volume}, "
        f"price_open={position.price_open}, "
        f"price_current={position.price_current}, "
        f"profit={position.profit}, "
        f"time={position.time}"
    )


def main() -> None:
    print("Starting MT5 WTI-BRENT live monitor...")
    print()

    login = int(input("Enter MT5 login: ").strip())
    password = input("Enter MT5 password: ").strip()
    server = input("Enter MT5 server: ").strip()

    initialize_mt5(login, password, server)

    print()
    print(f"WTI symbol: {WTI_SYMBOL}")
    print(f"BRENT symbol: {BRENT_SYMBOL}")
    print(f"Pair lot size: {PAIR_LOT_SIZE}")
    print(f"Entry spread alert level: {ENTRY_SPREAD}")
    print(f"Check interval: {CHECK_INTERVAL_SECONDS} second(s)")
    print("-" * 100)

    wti_quote, brent_quote = get_wti_brent_quotes(WTI_SYMBOL, BRENT_SYMBOL)
    display_spread = calculate_spread(wti_quote.mid, brent_quote.mid)
    executable_spread = get_executable_short_spread(WTI_SYMBOL, BRENT_SYMBOL)

    spread_state = detect_open_spread_state(WTI_SYMBOL, BRENT_SYMBOL)

    print("CURRENT MARKET SNAPSHOT")
    print(
        f"WTI   | bid={wti_quote.bid:.3f} ask={wti_quote.ask:.3f} mid={wti_quote.mid:.3f} "
        f"| tick={wti_quote.tick_time}"
    )
    print(
        f"BRENT | bid={brent_quote.bid:.3f} ask={brent_quote.ask:.3f} mid={brent_quote.mid:.3f} "
        f"| tick={brent_quote.tick_time}"
    )
    print(f"SPREAD | display={display_spread:.3f} | executable_short={executable_spread:.3f}")
    print("-" * 100)

    print("OPEN SPREAD STATE")
    print(f"  state: {spread_state['state']}")
    print_position_info("WTI", spread_state["wti_position"])
    print_position_info("BRENT", spread_state["brent_position"])
    print("-" * 100)

    if ENABLE_ALERTS and is_entry_signal(executable_spread, ENTRY_SPREAD):
        send_console_alert(
            f"Executable short spread reached {executable_spread:.3f} "
            f"(threshold: {ENTRY_SPREAD})"
        )

    open_pair = input(
        f"Do you want to open the SHORT spread pair now? "
        f"(Buy {WTI_SYMBOL} + Sell {BRENT_SYMBOL}, volume {PAIR_LOT_SIZE}) (yes/no): "
    ).strip().lower()

    if open_pair == "yes":
        print("Opening the WTI-BRENT short spread pair...")

        pair_result = open_short_spread_pair(
            wti_symbol=WTI_SYMBOL,
            brent_symbol=BRENT_SYMBOL,
            volume=PAIR_LOT_SIZE,
        )

        print(f"PAIR OPEN STATUS: {pair_result['stage']}")
        print("-" * 100)

        if pair_result["wti_result"] is not None:
            print_order_result("WTI BUY RESULT", pair_result["wti_result"])

        if pair_result["brent_result"] is not None:
            print_order_result("BRENT SELL RESULT", pair_result["brent_result"])

        if pair_result["rollback_result"] is not None:
            print_order_result("ROLLBACK WTI CLOSE RESULT", pair_result["rollback_result"])

        if pair_result["success"]:
            close_pair = input(
                "Do you want to close the WTI-BRENT short spread pair now? (yes/no): "
            ).strip().lower()

            if close_pair == "yes":
                print("Closing the WTI-BRENT short spread pair...")

                close_result = close_short_spread_pair(
                    wti_symbol=WTI_SYMBOL,
                    brent_symbol=BRENT_SYMBOL,
                    wti_position_ticket=pair_result["wti_result"].order,
                    brent_position_ticket=pair_result["brent_result"].order,
                    volume=PAIR_LOT_SIZE,
                )

                print_order_result("WTI CLOSE RESULT", close_result["wti_close_result"])
                print_order_result("BRENT CLOSE RESULT", close_result["brent_close_result"])

                print(f"PAIR CLOSE SUCCESS: {close_result['success']}")
                print("-" * 100)
            else:
                print("Leaving the WTI-BRENT pair open.")
                print("-" * 100)
        else:
            print("Pair did not open successfully.")
            print("-" * 100)
    else:
        print("Skipping manual pair open.")
        print("-" * 100)

    previous_wti_tick_time = None
    previous_brent_tick_time = None

    try:
        while True:
            wti_quote, brent_quote = get_wti_brent_quotes(WTI_SYMBOL, BRENT_SYMBOL)

            display_spread = calculate_spread(wti_quote.mid, brent_quote.mid)
            executable_spread = get_executable_short_spread(WTI_SYMBOL, BRENT_SYMBOL)

            wti_changed = previous_wti_tick_time != wti_quote.tick_time
            brent_changed = previous_brent_tick_time != brent_quote.tick_time

            wti_status = "UPDATED" if wti_changed else "STALE"
            brent_status = "UPDATED" if brent_changed else "STALE"

            print(
                f"WTI   | bid={wti_quote.bid:.3f} ask={wti_quote.ask:.3f} mid={wti_quote.mid:.3f} "
                f"| tick={wti_quote.tick_time} | {wti_status}"
            )
            print(
                f"BRENT | bid={brent_quote.bid:.3f} ask={brent_quote.ask:.3f} mid={brent_quote.mid:.3f} "
                f"| tick={brent_quote.tick_time} | {brent_status}"
            )
            print(
                f"SPREAD | display={display_spread:.3f} | executable_short={executable_spread:.3f}"
            )
            print("-" * 100)

            if ENABLE_ALERTS and is_entry_signal(executable_spread, ENTRY_SPREAD):
                send_console_alert(
                    f"Executable short spread reached {executable_spread:.3f} "
                    f"(threshold: {ENTRY_SPREAD})"
                )

            previous_wti_tick_time = wti_quote.tick_time
            previous_brent_tick_time = brent_quote.tick_time

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        shutdown_mt5()
        print("MT5 connection closed.")


if __name__ == "__main__":
    main()