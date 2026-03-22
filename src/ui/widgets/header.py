"""
ui/widgets/header.py — ASCII art header for the Plans dashboard.

Switches between MORNING and EVENING art at 18:00.
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

PLANS_SUB = "P  L  A  N  S"

class HeaderWidget(Widget):
    """Renders the Plans logo. Shows 'MORNING' art before 18:00, 'EVENING' after."""

    def render(self) -> RenderResult:
        hour = datetime.now().hour
        art = MORNING_ART if hour < 18 else EVENING_ART
        text = Text(art, style="bold cyan")
        text.append(f"\n{PLANS_SUB.center(62)}\n", style="bold white")
        return text
