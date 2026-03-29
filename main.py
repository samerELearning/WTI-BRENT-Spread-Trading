"""
Main runner for the WTI-Brent live spread monitor.
"""

from __future__ import annotations

import time
from datetime import datetime
from getpass import getpass

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
    get_wti_brent_prices,
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
    print("-" * 60)

    try:
        while True:
            wti_price, brent_price = get_wti_brent_prices(WTI_SYMBOL, BRENT_SYMBOL)

            display_spread = calculate_spread(wti_price, brent_price)
            executable_spread = get_executable_short_spread(WTI_SYMBOL, BRENT_SYMBOL)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(
                f"[{timestamp}] "
                f"WTI: {wti_price:.3f} | "
                f"Brent: {brent_price:.3f} | "
                f"Display Spread: {display_spread:.3f} | "
                f"Executable Short Spread: {executable_spread:.3f}"
            )

            if ENABLE_ALERTS and is_entry_signal(executable_spread, ENTRY_SPREAD):
                send_console_alert(
                    f"Executable short spread reached {executable_spread:.3f} "
                    f"(threshold: {ENTRY_SPREAD})"
                )

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        shutdown_mt5()
        print("MT5 connection closed.")


if __name__ == "__main__":
    main()