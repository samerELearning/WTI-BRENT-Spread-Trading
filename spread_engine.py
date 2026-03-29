"""
Spread calculation and signal evaluation logic.
"""


def calculate_spread(wti_price: float, brent_price: float) -> float:
    """
    Calculate the Brent-WTI spread.

    Args:
        wti_price (float): Latest WTI price.
        brent_price (float): Latest Brent price.

    Returns:
        float: Spread value (Brent - WTI).
    """
    return brent_price - wti_price


def is_entry_signal(spread: float, entry_spread: float) -> bool:
    """
    Check whether the spread has reached or exceeded the alert threshold.

    Args:
        spread (float): Current spread value.
        entry_spread (float): Alert threshold.

    Returns:
        bool: True if alert condition is met, otherwise False.
    """
    return spread >= entry_spread