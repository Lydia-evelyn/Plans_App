"""
ui/app.py — Entry point for the Plans TUI application.

PlansApp registers all screens, defines global key bindings (H/T/P/Q),
and handles Enter-to-dismiss for notification toasts.
"""

from textual.app import App
from src.ui.screens.dashboard import DashboardScreen
from src.ui.screens.habits import HabitsScreen
from src.ui.screens.tasks import TasksScreen
from src.ui.screens.projects import ProjectsScreen


class PlansApp(App):
    """The root Textual application. Pushes DashboardScreen on startup."""
    BINDINGS = [
        ("h", "push_screen('habits')", "Habits"),
        ("t", "push_screen('tasks')", "Tasks"),
        ("p", "push_screen('projects')", "Projects"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        background: #0d0d0d;
        color: #e0e0e0;
    }
    HeaderWidget {
        height: auto;
        padding: 1 2;
    }
    AnimalWidget {
        height: auto;
        padding: 0 2;
    }
    CalendarWidget {
        width: 26;
        height: auto;
        padding: 1;
        border: round #333333;
    }
    HabitsWidget {
        width: 1fr;
        height: auto;
        padding: 1;
        border: round #333333;
    }
    TasksWidget {
        width: 1fr;
        height: auto;
        padding: 1;
        border: round #333333;
    }
    Input {
        margin: 1 2;
        border: tall #444444;
        background: #1a1a1a;
    }
    Button {
        margin: 1 2;
    }
    Footer {
        background: #1a1a1a;
    }
    """

    SCREENS = {
        "dashboard": DashboardScreen,
        "habits":    HabitsScreen,
        "tasks":     TasksScreen,
        "projects":  ProjectsScreen,
    }

    def on_mount(self):
        self.push_screen("dashboard")

    def on_key(self, event) -> None:
        """Dismiss the oldest visible toast when Enter is pressed (if any exist)."""
        if event.key == "enter":
            try:
                from textual.widgets._toast import Toast
                toasts = self.query(Toast)
                if toasts:
                    toasts.first().remove()
                    event.stop()
            except Exception:
                pass
