from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input, Footer, Button
from textual.containers import Horizontal
from rich.text import Text

from src.models.checklist import get_checklist, add_checklist_item, complete_checklist_item, delete_checklist_item


class ChecklistScreen(Screen):
    def __init__(self, parent_id, parent_type, parent_name):
        super().__init__()
        self.parent_id = parent_id
        self.parent_type = parent_type
        self.parent_name = parent_name

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("a", "add_item", "Add"),
        ("q", "pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        text = Text()
        text.append(f"{self.parent_name}\n", style="bold cyan")
        text.append("─" * 40 + "\n", style="dim white")
        yield Static(text, id="checklist-header")
        yield Static(self._render_items(), id="checklist-list")
        yield Footer()

    def _render_items(self):
        items = get_checklist(self.parent_id, self.parent_type)
        text = Text()
        for i, item in enumerate(items):
            box = "[x]" if item['completed'] else "[ ]"
            text.append(f"  {i+1}. {box} {item['name']}\n", style="green" if item['completed'] else "white")
        if not items:
            text.append("  No items yet. Press [a] to add one.\n", style="dim white")
        return text

    def refresh_list(self):
        self.query_one("#checklist-list").update(self._render_items())

    def action_add_item(self):
        self.app.push_screen(AddChecklistItemScreen(), callback=self.on_item_added)

    def on_item_added(self, result):
        if result:
            add_checklist_item(self.parent_id, self.parent_type, result)
            self.refresh_list()


class AddChecklistItemScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Add Checklist Item\n──────────────────\n")
        yield Input(placeholder="Item name", id="item-name")
        with Horizontal():
            yield Button("Add", id="confirm", variant="success")
            yield Button("Cancel", id="cancel", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            name = self.query_one("#item-name", Input).value
            if name:
                self.dismiss(name)
        elif event.button.id == "cancel":
            self.dismiss(None)
