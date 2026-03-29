"""
Main runner for the WTI-Brent live spread monitor.
"""

from __future__ import annotations

import time

from alerts import send_console_alert
from config import (
    BRENT_SYMBOL,
    CHECK_INTERVAL_SECONDS,
    ENABLE_ALERTS,
    ENTRY_SPREAD,
    WTI_SYMBOL,
)
from price_fetcher import (
    get_executable_short_spread,
    get_wti_brent_quotes,
    initialize_mt5,
    shutdown_mt5,
)
from spread_engine import calculate_spread, is_entry_signal


def main() -> None:
    print("Starting MT5 WTI-Brent live monitor...")
    print()

    login = int(input("Enter MT5 login: ").strip())
    password = input("Enter MT5 password: ").strip()
    server = input("Enter MT5 server: ").strip()

    initialize_mt5(login, password, server)

    print()
    print(f"WTI symbol: {WTI_SYMBOL}")
    print(f"Brent symbol: {BRENT_SYMBOL}")
    print(f"Entry spread alert level: {ENTRY_SPREAD}")
    print(f"Check interval: {CHECK_INTERVAL_SECONDS} second(s)")
    print("-" * 80)

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
            print("-" * 80)

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