from textual.app import ComposeResult
from textual.widgets import Static, Input, Footer, Button, ListView, ListItem, Label
from textual.containers import Horizontal
from rich.text import Text

from src.ui.screens.base import BaseScreen, BaseAddScreen, ConfirmScreen
from src.models.habits import get_all_habits, add_habit, toggle_habit, delete_habit
from src.database import get_connection
from src.utils.date import today


class HabitsScreen(BaseScreen):
    BINDINGS = [
        ("a", "add_habit", "Add"),
        ("d", "delete_habit", "Delete"),
        ("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self._habits = []

    def _render_header(self):
        text = Text()
        text.append("H  A  B  I  T  S\n", style="bold magenta")
        text.append("─" * 40 + "\n", style="dim white")
        return text

    def _build_items(self):
        from src.utils.errors import PlanError
        try:
            conn = get_connection()
        except RuntimeError as e:
            raise PlanError(str(e))
        t = today()
        self._habits = get_all_habits()
        items = []
        for habit in self._habits:
            history = conn.execute(
                "SELECT completed FROM habit_history WHERE habit_id = ? AND date = ?",
                (habit['id'], t)
            ).fetchone()
            checked = history and history['completed']
            box = "✓" if checked else "○"
            label = f"  {box} {habit['name']}  ({habit['repeat']})  streak: {habit['streak']}"
            items.append(ListItem(Label(label, markup=False)))
        conn.close()
        return items

    def compose(self) -> ComposeResult:
        yield Static(self._render_header(), id="habits-header")
        yield ListView(id="habits-list")
        yield Footer()

    def on_mount(self):
        self.refresh_list()

    def refresh_list(self):
        try:
            lv = self.query_one("#habits-list", ListView)
            current = lv.index or 0
            lv.clear()
            for item in self._build_items():
                lv.append(item)
            if not self._habits:
                lv.mount(ListItem(Label("  No habits yet. Press 'a' to add one.", markup=False)))
            elif self._habits:
                lv.index = min(current, len(self._habits) - 1)
        except Exception as e:
            self.notify_error(e)

    def on_list_view_selected(self, event: ListView.Selected):
        try:
            lv = self.query_one("#habits-list", ListView)
            index = lv.index
            if index is not None and index < len(self._habits):
                toggle_habit(self._habits[index]['id'])
                self.refresh_list()
        except Exception as e:
            self.notify_error(e)

    def action_add_habit(self):
        self.app.push_screen(AddHabitScreen(), callback=self.on_habit_added)

    def action_delete_habit(self):
        lv = self.query_one("#habits-list", ListView)
        index = lv.index
        if index is not None and index < len(self._habits):
            habit = self._habits[index]
            self.app.push_screen(
                ConfirmScreen(f"Delete habit '{habit['name']}'? This will remove all history."),
                callback=lambda confirmed: self._on_delete_confirmed(confirmed, habit['id'])
            )

    def _on_delete_confirmed(self, confirmed, habit_id):
        if confirmed:
            try:
                delete_habit(habit_id)
                self.refresh_list()
            except Exception as e:
                self.notify_error(e)

    def on_habit_added(self, result):
        try:
            if result:
                add_habit(result['name'], result['repeat'])
                self.refresh_list()
        except Exception as e:
            self.notify_error(e)


class AddHabitScreen(BaseAddScreen):
    def compose(self) -> ComposeResult:
        yield Static("Add Habit\n─────────\n")
        yield Input(placeholder="Habit name", id="habit-name")
        yield Input(placeholder="Repeat (e.g. daily, weekly:mon,wed,fri)", id="habit-repeat")
        with Horizontal():
            yield Button("Add", id="confirm", variant="success")
            yield Button("Cancel", id="cancel", variant="error")
        yield Footer()

    def _submit(self):
        name = self.query_one("#habit-name", Input).value
        repeat = self.query_one("#habit-repeat", Input).value
        if name and repeat:
            self.dismiss({'name': name, 'repeat': repeat})

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "habit-name":
            self.query_one("#habit-repeat", Input).focus()
        elif event.input.id == "habit-repeat":
            self._submit()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self._submit()
        elif event.button.id == "cancel":
            self.dismiss(None)
