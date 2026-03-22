"""
ui/screens/base.py — Shared base classes for all Plans screens.

BaseScreen   — for main navigation screens. ESC pops back to the previous screen.
BaseAddScreen — for modal add/edit screens. ESC dismisses without saving.

Both provide notify_error() which displays a PlanError (or any exception)
as a red notification toast for 15 seconds.
"""

from textual.screen import Screen
from textual.widgets import Input, Button
from textual.containers import Horizontal


class BaseScreen(Screen):
    """Base for all main screens. Handles ESC to go back."""

    def on_key(self, event) -> None:
        if event.key == "escape":
            event.stop()
            self.app.pop_screen()

    def action_back(self):
        """Pop this screen off the stack (bound to ESC via BINDINGS on subclasses)."""
        self.app.pop_screen()

    def notify_error(self, e: Exception) -> None:
        """Show a red error toast for 15 seconds. Press Enter to dismiss early."""
        self.notify(str(e), severity="error", timeout=15)


class BaseAddScreen(Screen):
    """Base for all add/edit screens. Handles ESC to cancel."""

    def on_key(self, event) -> None:
        if event.key == "escape":
            event.stop()
            self.dismiss(None)

    def action_dismiss_cancel(self):
        self.dismiss(None)

    def notify_error(self, e: Exception) -> None:
        self.notify(str(e), severity="error", timeout=15)
