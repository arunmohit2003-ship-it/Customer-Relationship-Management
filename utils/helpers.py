"""
utils/helpers.py
------------------
Small, reusable helper functions shared across multiple views.
"""

from datetime import datetime, date


def center_window(win, width, height):
    """Center a Toplevel/Frame's window on the user's screen."""
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def format_date(value):
    """Format a date/datetime/str value as DD-Mon-YYYY for display."""
    if value is None or value == "":
        return "-"
    if isinstance(value, (datetime, date)):
        return value.strftime("%d-%b-%Y")
    return str(value)


def format_time(value):
    """Format a TIME column value (returned as timedelta by the MySQL
    driver) as a friendly 12-hour HH:MM AM/PM string."""
    if value is None or value == "":
        return "-"
    if hasattr(value, "seconds") and hasattr(value, "days"):
        total_seconds = value.seconds
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        suffix = "AM" if hours < 12 else "PM"
        display_hour = hours % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour:02d}:{minutes:02d} {suffix}"
    return str(value)
