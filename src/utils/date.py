"""
utils/date.py — Date helpers for Plans.

All dates are stored and displayed as DD-MM-YYYY strings throughout the app.
This module is the single source of truth for that format constant.
"""

from datetime import datetime

DATE_FORMAT = "%d-%m-%Y"


def today():
    """Return today's date as a DD-MM-YYYY string."""
    return datetime.now().strftime(DATE_FORMAT)

def now():
    """Return the current datetime object."""
    return datetime.now()

def parse(date_str):
    """Parse a DD-MM-YYYY string into a datetime object."""
    return datetime.strptime(date_str, DATE_FORMAT)

def display(date_str):
    """Format a DD-MM-YYYY string as a human-readable string, e.g. 'Monday, 16 March 2026'."""
    dt = parse(date_str)
    return dt.strftime("%A, %d %B %Y")
