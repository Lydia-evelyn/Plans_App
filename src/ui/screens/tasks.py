from textual.app import ComposeResult
from textual.widgets import Static, Input, Footer, Button, ListView, ListItem, Label
from textual.containers import Horizontal
from rich.text import Text

from src.ui.screens.base import BaseScreen, BaseAddScreen, ConfirmScreen
from src.models.tasks import get_all_tasks, add_task, complete_task, delete_task


class TasksScreen(BaseScreen):
    BINDINGS = [
        ("a", "add_task", "Add"),
        ("d", "delete_task", "Delete"),
        ("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self._tasks = []

    def _render_header(self):
        text = Text()
        text.append("T  A  S  K  S\n", style="bold blue")
        text.append("─" * 40 + "\n", style="dim white")
        return text

    def _build_items(self):
        self._tasks = get_all_tasks()
        items = []
        for task in self._tasks:
            due = f"  due {task['due']}" if task['due'] else ""
            if task['status'] == 'done':
                text = Text()
                text.append(f"  ✓ {task['name']}{due}", style="strike dim")
                items.append(ListItem(Label(text)))
            else:
                label = f"  ○ {task['name']}{due}"
                items.append(ListItem(Label(label, markup=False)))
        return items

    def compose(self) -> ComposeResult:
        yield Static(self._render_header(), id="tasks-header")
        yield ListView(id="tasks-list")
        yield Footer()

    def on_mount(self):
        self.refresh_list()

    def refresh_list(self):
        try:
            lv = self.query_one("#tasks-list", ListView)
            current = lv.index or 0
            lv.clear()
            for item in self._build_items():
                lv.append(item)
            if not self._tasks:
                lv.mount(ListItem(Label("  No tasks yet. Press 'a' to add one.", markup=False)))
            elif self._tasks:
                lv.index = min(current, len(self._tasks) - 1)
        except Exception as e:
            self.notify_error(e)

    def on_list_view_selected(self, event: ListView.Selected):
        try:
            lv = self.query_one("#tasks-list", ListView)
            index = lv.index
            if index is not None and index < len(self._tasks):
                complete_task(self._tasks[index]['id'])
                self.refresh_list()
        except Exception as e:
            self.notify_error(e)

    def action_add_task(self):
        self.app.push_screen(AddTaskScreen(), callback=self.on_task_added)

    def action_delete_task(self):
        lv = self.query_one("#tasks-list", ListView)
        index = lv.index
        if index is not None and index < len(self._tasks):
            task = self._tasks[index]
            self.app.push_screen(
                ConfirmScreen(f"Delete task '{task['name']}'?"),
                callback=lambda confirmed: self._on_delete_confirmed(confirmed, task['id'])
            )

    def _on_delete_confirmed(self, confirmed, task_id):
        if confirmed:
            try:
                delete_task(task_id)
                self.refresh_list()
            except Exception as e:
                self.notify_error(e)

    def on_task_added(self, result):
        try:
            if result:
                add_task(result['name'], due=result.get('due'))
                self.refresh_list()
        except Exception as e:
            self.notify_error(e)


class AddTaskScreen(BaseAddScreen):
    def compose(self) -> ComposeResult:
        yield Static("Add Task\n────────\n")
        yield Input(placeholder="Task name", id="task-name")
        yield Input(placeholder="Due date (DD-MM-YYYY) optional", id="task-due")
        with Horizontal():
            yield Button("Add", id="confirm", variant="success")
            yield Button("Cancel", id="cancel", variant="error")
        yield Footer()

    def _submit(self):
        name = self.query_one("#task-name", Input).value
        due = self.query_one("#task-due", Input).value or None
        if name:
            self.dismiss({'name': name, 'due': due})

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "task-name":
            self.query_one("#task-due", Input).focus()
        elif event.input.id == "task-due":
            self._submit()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self._submit()
        elif event.button.id == "cancel":
            self.dismiss(None)
