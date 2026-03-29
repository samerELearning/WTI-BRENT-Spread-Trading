"""
Main runner for the WTI-Brent live spread monitor.
"""

import time
from datetime import datetime

from config import (
    ENTRY_SPREAD,
    CHECK_INTERVAL_SECONDS,
    WTI_SYMBOL,
    BRENT_SYMBOL,
    ENABLE_ALERTS,
)
from price_fetcher import get_wti_brent_prices
from spread_engine import calculate_spread, is_entry_signal
from alerts import send_console_alert


def main() -> None:
    """
    Start the live spread monitoring loop.
    """
    print("Starting WTI-Brent live spread monitor...")
    print(f"WTI symbol: {WTI_SYMBOL}")
    print(f"Brent symbol: {BRENT_SYMBOL}")
    print(f"Entry spread alert level: {ENTRY_SPREAD}")
    print(f"Check interval: {CHECK_INTERVAL_SECONDS} seconds")
    print("-" * 50)

    while True:
        try:
            wti_price, brent_price = get_wti_brent_prices(WTI_SYMBOL, BRENT_SYMBOL)
            spread = calculate_spread(wti_price, brent_price)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(
                f"[{now}] "
                f"WTI: {wti_price:.2f} | "
                f"Brent: {brent_price:.2f} | "
                f"Spread: {spread:.2f}"
            )

            if ENABLE_ALERTS and is_entry_signal(spread, ENTRY_SPREAD):
                send_console_alert(
                    f"Spread threshold reached. Current spread = {spread:.2f}"
                )

        except Exception as error:
            print(f"Error: {error}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()