"""
Alert utilities for the WTI-Brent spread monitor.
"""


def send_console_alert(message: str) -> None:
    """
    Display an alert message in the console.

    Args:
        message (str): Alert text to display.
    """
    print(f"ALERT: {message}")