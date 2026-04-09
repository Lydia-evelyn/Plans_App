"""
ui/screens/base.py — Shared base classes for all Plans screens.

BaseScreen    — for main navigation screens. ESC pops back to the previous screen.
BaseAddScreen — for modal add/edit screens. ESC dismisses without saving.
ConfirmScreen — a reusable yes/no confirmation modal. Press Y/N or use buttons.

Both BaseScreen and BaseAddScreen provide notify_error() which displays a
PlanError (or any exception) as a red notification toast for 15 seconds.
"""

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Input, Button
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


class ConfirmScreen(Screen):
    """A reusable yes/no confirmation modal.

    Dismisses with True if confirmed, False if cancelled.
    Press Y to confirm, N or ESC to cancel.
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Static(f"\n  {self.message}\n", id="confirm-message")
        with Horizontal():
            yield Button("Yes  [Y]", id="yes", variant="error")
            yield Button("No  [N]", id="no", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def on_key(self, event) -> None:
        if event.key == "y":
            event.stop()
            self.dismiss(True)
        elif event.key in ("n", "escape"):
            event.stop()
            self.dismiss(False)
