from textual.app import ComposeResult
from textual.widgets import Static, Input, Footer, Button
from textual.containers import Horizontal
from rich.text import Text

from src.ui.screens.base import BaseScreen, BaseAddScreen
from src.models.projects import get_all_projects, add_project, archive_project
from src.models.tasks import get_all_tasks, add_task
from src.models.checklist import get_checklist_progress


class ProjectsScreen(BaseScreen):
    BINDINGS = [
        ("a", "add_project", "Add"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(self._render_header(), id="projects-header")
        yield Static(self._render_projects(), id="projects-list")
        yield Footer()

    def _render_header(self):
        text = Text()
        text.append("P  R  O  J  E  C  T  S\n", style="bold yellow")
        text.append("─" * 40 + "\n", style="dim white")
        return text

    def _render_projects(self):
        projects = get_all_projects()
        text = Text()
        for i, project in enumerate(projects):
            text.append(f"  {i+1}. {project['name']}  [{project['status']}]\n", style="white")
        if not projects:
            text.append("  No projects yet. Press [a] to add one.\n", style="dim white")
        return text

    def refresh_list(self):
        self.query_one("#projects-list").update(self._render_projects())

    def action_add_project(self):
        self.app.push_screen(AddProjectScreen(), callback=self.on_project_added)

    def on_project_added(self, result):
        if result:
            add_project(result['name'], result.get('header_style', 'block'))
            self.refresh_list()


class AddProjectScreen(BaseAddScreen):
    def compose(self) -> ComposeResult:
        yield Static("Add Project\n───────────\n")
        yield Input(placeholder="Project name", id="project-name")
        yield Input(placeholder="Header style (block/thin/shadow)", id="project-style")
        with Horizontal():
            yield Button("Add", id="confirm", variant="success")
            yield Button("Cancel", id="cancel", variant="error")
        yield Footer()

    def _submit(self):
        name = self.query_one("#project-name", Input).value
        style = self.query_one("#project-style", Input).value or 'block'
        if name:
            self.dismiss({'name': name, 'header_style': style})

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "project-name":
            self.query_one("#project-style", Input).focus()
        elif event.input.id == "project-style":
            self._submit()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self._submit()
        elif event.button.id == "cancel":
            self.dismiss(None)


class ProjectTasksScreen(BaseScreen):
    def __init__(self, project):
        super().__init__()
        self.project = project

    BINDINGS = [
        ("a", "add_task", "Add Task"),
        ("escape", "back", "Back"),
        ("q", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        text = Text()
        text.append(f"{self.project['name'].upper()}\n", style="bold yellow")
        text.append("─" * 40 + "\n", style="dim white")
        yield Static(text, id="project-header")
        yield Static(self._render_tasks(), id="project-tasks")
        yield Footer()

    def _render_tasks(self):
        tasks = get_all_tasks(project_id=self.project['id'])
        text = Text()
        for i, task in enumerate(tasks):
            completed, total = get_checklist_progress(task['id'], 'task')
            progress = f" ({completed}/{total})" if total > 0 else ""
            due = f"  due {task['due']}" if task['due'] else ""
            if task['status'] == 'done':
                text.append(f"  {i+1}. [x] {task['name']}{progress}{due}\n", style="strike dim")
            else:
                text.append(f"  {i+1}. [ ] {task['name']}{progress}{due}\n", style="white")
        if not tasks:
            text.append("  No tasks yet. Press [a] to add one.\n", style="dim white")
        return text

    def refresh_list(self):
        self.query_one("#project-tasks").update(self._render_tasks())

    def action_add_task(self):
        from src.ui.screens.tasks import AddTaskScreen
        self.app.push_screen(AddTaskScreen(), callback=self.on_task_added)

    def on_task_added(self, result):
        if result:
            add_task(result['name'], project_id=self.project['id'], due=result.get('due'))
            self.refresh_list()
