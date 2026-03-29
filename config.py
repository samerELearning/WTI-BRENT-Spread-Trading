"""
Configuration values for the WTI-Brent live spread monitor.

This file contains adjustable project settings such as:
- market symbols
- spread alert threshold
- polling interval
- feature toggles
"""

ENTRY_SPREAD = 9.0          #alert me if Brent - WTI reaches 9
CHECK_INTERVAL_SECONDS = 60 #check every 60 seconds

WTI_SYMBOL = "CL=F"         #Yahoo Finance code for WTI futures
BRENT_SYMBOL = "BZ=F"       #Yahoo Finance code for Brent futures

PRICE_INTERVAL = "1m"       # Candle granularity
PRICE_PERIOD = "1d"         # Historical window requested

FALLBACK_PRICE_INTERVAL = "5m"
FALLBACK_PRICE_PERIOD = "5d"

LAST_RESORT_PRICE_INTERVAL = "1d"
LAST_RESORT_PRICE_PERIOD = "1mo"

ENABLE_ALERTS = True        #allow the app to trigger alerts