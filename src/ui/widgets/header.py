"""
ui/widgets/header.py — ASCII art header for the Plans dashboard.

Shows MORNING art before 12:00, EVENING art from 12:00–18:00, and
NIGHT art from 18:00 onwards. A greeting line below the logo reflects
the time of day: Good Morning / Good Afternoon / Good Night.
"""

from textual.widget import Widget
from textual.app import RenderResult
from rich.text import Text
from datetime import datetime

MORNING_ART = """
███╗░░░███╗░█████╗░██████╗░███╗░░██╗██╗███╗░░██╗░██████╗░██╗
████╗░████║██╔══██╗██╔══██╗████╗░██║██║████╗░██║██╔════╝░██║
██╔████╔██║██║░░██║██████╔╝██╔██╗██║██║██╔██╗██║██║░░██╗░██║
██║╚██╔╝██║██║░░██║██╔══██╗██║╚████║██║██║╚████║██║░░╚██║╚═╝
██║░╚═╝░██║╚█████╔╝██║░░██║██║░╚███║██║██║░╚███║╚██████╔╝██╗
╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░╚══╝░╚═════╝░╚═╝"""

EVENING_ART = """
███████╗██╗░░░██╗███████╗███╗░░██╗██╗███╗░░██╗░██████╗░██╗
██╔════╝██║░░░██║██╔════╝████╗░██║██║████╗░██║██╔════╝░██║
█████╗░░╚██╗░██╔╝█████╗░░██╔██╗██║██║██╔██╗██║██║░░██╗░██║
██╔══╝░░░╚████╔╝░██╔══╝░░██║╚████║██║██║╚████║██║░░╚██║╚═╝
███████╗░░╚██╔╝░░███████╗██║░╚███║██║██║░╚███║╚██████╔╝██╗
╚══════╝░░░╚═╝░░░╚══════╝╚═╝░░╚══╝╚═╝╚═╝░░╚══╝░╚═════╝░╚═╝"""

NIGHT_ART = """
███╗░░██╗██╗░██████╗░██╗░░██╗████████╗██╗
████╗░██║██║██╔════╝░██║░░██║╚══██╔══╝██║
██╔██╗██║██║██║░░██╗░███████║░░░██║░░░██║
██║╚████║██║██║░░╚██║██╔══██║░░░██║░░░╚═╝
██║░╚███║██║╚██████╔╝██║░░██║░░░██║░░░██╗
╚═╝░░╚══╝╚═╝░╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝"""

PLANS_SUB = "P  L  A  N  S"


class HeaderWidget(Widget):
    """Renders the Plans logo with a time-based greeting.

    Before 12:00  — MORNING art, 'Good Morning'
    12:00–18:00   — EVENING art, 'Good Afternoon'
    18:00 onwards — NIGHT art,   'Good Night'
    """

    def render(self) -> RenderResult:
        hour = datetime.now().hour
        if hour < 12:
            art = MORNING_ART
            greeting = "Good Morning"
        elif hour < 18:
            art = EVENING_ART
            greeting = "Good Afternoon"
        else:
            art = NIGHT_ART
            greeting = "Good Night"
        text = Text(art, style="bold cyan")
        text.append(f"\n{PLANS_SUB.center(62)}\n", style="bold white")
        text.append(f"{'— ' + greeting + ' —'.center(62)}\n", style="dim white")
        return text
