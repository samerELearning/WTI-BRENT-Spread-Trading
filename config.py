"""
Configuration values for the WTI-Brent live spread monitor.

This file contains adjustable project settings such as:
- market symbols
- spread alert threshold
- polling interval
- feature toggles
"""

ENTRY_SPREAD = 9.0          # alert when Brent - WTI reaches this level
CHECK_INTERVAL_SECONDS = 1  # check every 1 second

WTI_SYMBOL = "WTI"
BRENT_SYMBOL = "BRENT"

ENABLE_ALERTS = True

MT5_TERMINAL_PATH = r"C:\Program Files\FxPro - MetaTrader 5\terminal64.exe"