"""
ui/screens/projects.py — Projects screen and project task detail screen.

ProjectsScreen     — lists all active projects; arrow keys to navigate, Enter to open.
AddProjectScreen   — modal for creating a new project.
ProjectTasksScreen — full-screen view of a single project's tasks.
                     Arrow keys to navigate, Space/Enter to complete, D to delete.
"""

from textual.app import ComposeResult
from textual.widgets import Static, Input, Footer, Button
from textual.containers import Horizontal
from textual.reactive import reactive
from rich.text import Text

from src.ui.screens.base import BaseScreen, BaseAddScreen, ConfirmScreen
from src.models.projects import get_all_projects, add_project, delete_project
from src.models.tasks import get_all_tasks, add_task, complete_task, delete_task
from src.models.checklist import get_checklist_progress


class ProjectsScreen(BaseScreen):
    BINDINGS = [
        ("a", "add_project", "Add"),
        ("d", "delete_project", "Delete"),
        ("escape", "back", "Back"),
    ]

    selected: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        yield Static(self._render_header(), id="projects-header")
        yield Static(self._render_projects(), id="projects-list")
        yield Footer()

    def _render_header(self):
        text = Text()
        text.append("P  R  O  J  E  C  T  S\n", style="bold yellow")
        text.append("─" * 40 + "\n", style="dim white")
        return text

    def _get_projects(self):
        return get_all_projects()

    def _render_projects(self):
        projects = self._get_projects()
        text = Text()
        for i, project in enumerate(projects):
            if i == self.selected:
                text.append(f"  ▶ {project['name']}  [{project['status']}]\n", style="bold yellow")
            else:
                text.append(f"    {project['name']}  [{project['status']}]\n", style="white")
        if not projects:
            text.append("  No projects yet. Press [a] to add one.\n", style="dim white")
        return text

    def watch_selected(self, value: int) -> None:
        try:
            self.query_one("#projects-list").update(self._render_projects())
        except Exception:
            pass

    def refresh_list(self):
        self.query_one("#projects-list").update(self._render_projects())

    def on_screen_resume(self):
        self.refresh_list()

    def on_key(self, event) -> None:
        projects = self._get_projects()
        if event.key == "up":
            event.stop()
            if projects:
                self.selected = max(0, self.selected - 1)
        elif event.key == "down":
            event.stop()
            if projects:
                self.selected = min(len(projects) - 1, self.selected + 1)
        elif event.key == "enter":
            event.stop()
            if projects and self.selected < len(projects):
                self.app.push_screen(ProjectTasksScreen(projects[self.selected]))
        elif event.key == "escape":
            event.stop()
            self.app.pop_screen()

    def action_add_project(self):
        self.app.push_screen(AddProjectScreen(), callback=self.on_project_added)

    def action_delete_project(self):
        projects = self._get_projects()
        if projects and self.selected < len(projects):
            project = projects[self.selected]
            self.app.push_screen(
                ConfirmScreen(f"Delete '{project['name']}' and all its tasks?"),
                callback=lambda confirmed: self._on_delete_confirmed(confirmed, project['id'])
            )

    def _on_delete_confirmed(self, confirmed, project_id):
        if confirmed:
            try:
                delete_project(project_id)
                self.selected = max(0, self.selected - 1)
                self.refresh_list()
            except Exception as e:
                self.notify_error(e)

    def on_project_added(self, result):
        if result:
            try:
                add_project(result['name'], result.get('header_style', 'block'))
                self.refresh_list()
            except Exception as e:
                self.notify_error(e)


class AddProjectScreen(BaseAddScreen):
    def compose(self) -> ComposeResult:
        yield Static("Add Project\n───────────\n")
        yield Input(placeholder="Project name", id="project-name")
        yield Input(placeholder="Header style: elegant / retro / basic / block", id="project-style")
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
    BINDINGS = [
        ("a", "add_task", "Add Task"),
        ("d", "delete_task", "Delete"),
        ("escape", "back", "Back"),
    ]

    selected: reactive[int] = reactive(0)

    def __init__(self, project):
        super().__init__()
        self.project = project

    def _render_header(self):
        name = self.project['name'].upper()
        style = self.project['header_style'] if self.project['header_style'] else 'block'
        width = 40
        text = Text()

        if style == 'elegant':
            # Textured borders with spaced letters and ◈ accents
            spaced = ' '.join(name)
            inner = f"  ◈  {spaced}  ◈  "
            padded = inner.ljust(width - 2)[:width - 2]
            text.append("▌" + "░" * (width - 2) + "▐\n", style="bold yellow")
            text.append(f"▌{padded}▐\n", style="bold yellow")
            text.append("▌" + "░" * (width - 2) + "▐\n", style="bold yellow")

        elif style == 'retro':
            # Arrow accent with heavy rounded underline
            text.append(f"  ▸ {name}\n", style="bold yellow")
            text.append(f"  ┕{'━' * (width - 4)}┙\n", style="yellow")

        elif style == 'basic':
            # Dashed bookends: ---- MY PROJECT ----
            dash_count = max(2, (width - len(name) - 4) // 2)
            text.append(f"  {'─' * dash_count}  {name}  {'─' * dash_count}\n", style="bold yellow")

        elif style == 'block':
            # Solid filled box — 30 chars of █ to the left of the name
            left_fill = 30
            name_section = f"  {name}  "
            right_fill = max(4, 56 - left_fill - len(name_section))
            total = left_fill + len(name_section) + right_fill
            text.append("█" * total + "\n", style="bold yellow")
            text.append("█" * left_fill + name_section + "█" * right_fill + "\n", style="bold yellow")
            text.append("█" * total + "\n", style="bold yellow")

        else:
            text.append(f"  {name}\n", style="bold yellow")
            text.append("  " + "─" * (width - 2) + "\n", style="dim white")

        return text

    def compose(self) -> ComposeResult:
        yield Static(self._render_header(), id="project-header")
        yield Static(self._render_tasks(), id="project-tasks")
        yield Footer()

    def _get_tasks(self):
        return get_all_tasks(project_id=self.project['id'])

    def _render_tasks(self):
        tasks = self._get_tasks()
        text = Text()
        for i, task in enumerate(tasks):
            completed, total = get_checklist_progress(task['id'], 'task')
            progress = f" ({completed}/{total})" if total > 0 else ""
            due = f"  due {task['due']}" if task['due'] else ""
            done = task['status'] == 'done'
            box = "✓" if done else "○"
            cursor = "▶ " if i == self.selected else "  "
            line = f"  {cursor}{box} {task['name']}{progress}{due}\n"
            if done:
                text.append(line, style="strike dim")
            elif i == self.selected:
                text.append(line, style="bold yellow")
            else:
                text.append(line, style="white")
        if not tasks:
            text.append("  No tasks yet. Press [a] to add one.\n", style="dim white")
        return text

    def watch_selected(self, value: int) -> None:
        try:
            self.query_one("#project-tasks").update(self._render_tasks())
        except Exception:
            pass

    def refresh_list(self):
        self.query_one("#project-tasks").update(self._render_tasks())

    def on_key(self, event) -> None:
        tasks = self._get_tasks()
        if event.key == "up":
            event.stop()
            if tasks:
                self.selected = max(0, self.selected - 1)
        elif event.key == "down":
            event.stop()
            if tasks:
                self.selected = min(len(tasks) - 1, self.selected + 1)
        elif event.key in ("enter", "space"):
            event.stop()
            if tasks and self.selected < len(tasks):
                task = tasks[self.selected]
                if task['status'] == 'open':
                    try:
                        complete_task(task['id'])
                        self.refresh_list()
                    except Exception as e:
                        self.notify_error(e)
        elif event.key == "escape":
            event.stop()
            self.app.pop_screen()

    def action_add_task(self):
        from src.ui.screens.tasks import AddTaskScreen
        self.app.push_screen(AddTaskScreen(), callback=self.on_task_added)

    def on_task_added(self, result):
        if result:
            try:
                add_task(result['name'], project_id=self.project['id'], due=result.get('due'))
                self.refresh_list()
            except Exception as e:
                self.notify_error(e)

    def action_delete_task(self):
        tasks = self._get_tasks()
        if tasks and self.selected < len(tasks):
            try:
                delete_task(tasks[self.selected]['id'])
                self.selected = max(0, self.selected - 1)
                self.refresh_list()
            except Exception as e:
                self.notify_error(e)
