from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static, Footer
from textual.containers import Horizontal, VerticalScroll
from rich.text import Text

from src.ui.widgets.header import HeaderWidget
from src.ui.widgets.calendar import CalendarWidget
from src.ui.widgets.animal import AnimalWidget
from src.models.habits import get_all_habits
from src.models.tasks import get_all_tasks
from src.models.checklist import get_checklist_progress
from src.database import get_connection
from src.utils.date import today


class HabitsWidget(Static):
    def on_mount(self):
        self.refresh_habits()

    def refresh_habits(self):
        conn = get_connection()
        t = today()
        habits = get_all_habits()
        text = Text()
        text.append("HABITS\n", style="bold magenta")
        text.append("─" * 26 + "\n", style="dim white")
        for habit in habits:
            history = conn.execute(
                "SELECT completed FROM habit_history WHERE habit_id = ? AND date = ?",
                (habit['id'], t)
            ).fetchone()
            checked = history and history['completed']
            box = "✓" if checked else "○"
            completed, total = get_checklist_progress(habit['id'], 'habit')
            progress = f" ({completed}/{total})" if total > 0 else ""
            text.append(f"  {box} {habit['name']}{progress}\n", style="bold green" if checked else "white")
        text.append("\n")
        text.append("  streaks\n", style="dim white")
        for habit in habits:
            text.append(f"  {habit['name'][:16]:<16} ", style="dim white")
            text.append("█" * min(habit['streak'], 10), style="bold magenta")
            text.append(f" {habit['streak']}d\n", style="dim white")
        conn.close()
        self.update(text)


class TasksWidget(Static):
    def on_mount(self):
        self.refresh_tasks()

    def refresh_tasks(self):
        tasks = get_all_tasks()
        text = Text()
        text.append("TODAY'S TASKS\n", style="bold blue")
        text.append("─" * 26 + "\n", style="dim white")
        for task in tasks:
            completed, total = get_checklist_progress(task['id'], 'task')
            progress = f" ({completed}/{total})" if total > 0 else ""
            due = f"\n       due {task['due']}" if task['due'] else ""
            done = task['status'] == 'done'
            box = "✓" if done else "○"
            style = "strike dim" if done else "white"
            text.append(f"  {box} {task['name']}{progress}{due}\n", style=style)
        self.update(text)


class DashboardScreen(Screen):
    BINDINGS = [
        ("h", "push_screen('habits')", "Habits"),
        ("t", "push_screen('tasks')", "Tasks"),
        ("p", "push_screen('projects')", "Projects"),
        ("e", "export", "Export"),
        ("i", "import_md", "Import"),
        Binding("r", "refresh", "Refresh", priority=True),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield HeaderWidget()
            yield AnimalWidget()
            with Horizontal():
                yield CalendarWidget()
                yield HabitsWidget()
                yield TasksWidget()
        yield Footer()

    def on_screen_resume(self):
        self.call_after_refresh(self._do_refresh)

    def action_refresh(self):
        self._do_refresh()

    def _do_refresh(self):
        try:
            self.query_one(HabitsWidget).refresh_habits()
        except Exception as e:
            self.notify(f"Habits refresh failed: {e}", severity="error", timeout=15)
        try:
            self.query_one(TasksWidget).refresh_tasks()
        except Exception as e:
            self.notify(f"Tasks refresh failed: {e}", severity="error", timeout=15)

    def on_key(self, event) -> None:
        if event.key == "r":
            event.stop()
            self._do_refresh()

    def action_export(self):
        try:
            from src.logic.export import export_to_obsidian
            export_to_obsidian()
            self.notify("Exported to Obsidian.")
        except Exception as e:
            self.notify(str(e), severity="error", timeout=15)

    def action_import_md(self):
        try:
            from src.logic.import_md import import_from_obsidian
            warnings = import_from_obsidian()
            if warnings:
                for w in warnings:
                    self.notify(w, severity="warning", timeout=15)
            else:
                self.notify("Imported from Obsidian — everything matched.")
            self._do_refresh()
        except Exception as e:
            self.notify(str(e), severity="error", timeout=15)
