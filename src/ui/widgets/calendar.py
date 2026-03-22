"""
ui/widgets/calendar.py — Monthly calendar widget for the dashboard.

Highlights today's date in green. Rendered as a plain-text grid using
Python's standard calendar module.
"""

from textual.widget import Widget
from textual.app import RenderResult
from rich.text import Text
import calendar
from datetime import datetime

class CalendarWidget(Widget):
    """Displays a month-at-a-glance calendar. Today's date is highlighted in green."""

    def render(self) -> RenderResult:
        now = datetime.now()
        today = now.day
        text = Text()
        text.append(f"  {now.strftime('%B %Y')}\n", style="bold yellow")
        text.append("  Mo Tu We Th Fr Sa Su\n", style="dim white")
        for week in calendar.monthcalendar(now.year, now.month):
            line = "  "
            for day in week:
                if day == 0:
                    line += "   "
                elif day == today:
                    text.append(line)
                    text.append(f"[{day:2d}]", style="bold green")
                    line = ""
                else:
                    line += f"{day:3d}"
            text.append(line + "\n")
        return text
