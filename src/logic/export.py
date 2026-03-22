"""
logic/export.py — Export Plans data to an Obsidian-compatible Markdown file.

Writes to $PLANS_VAULT_PATH/plans.md in standard checkbox format:
  - [x] completed item
  - [ ] incomplete item

The file is overwritten on every export. Vault path is read from the
PLANS_VAULT_PATH environment variable (set in ~/.zshrc).
"""

import os
from src.database import get_connection
from src.utils.date import today
from src.utils.errors import PlanError
from src.models.checklist import get_checklist_progress

VAULT_PATH = os.path.expandvars(os.path.expanduser(
    os.environ.get('PLANS_VAULT_PATH', '~/Documents/ObsidianVault/plans')
))

def export_to_obsidian():
    """Write all habits, tasks, and project tasks to $PLANS_VAULT_PATH/plans.md.

    Creates the vault directory if it doesn't exist.
    Raises PlanError on missing vault path, OS errors, or DB errors.
    """
    if not VAULT_PATH:
        raise PlanError("PLANS_VAULT_PATH is not set. Add it to your ~/.zshrc and run 'source ~/.zshrc'.")

    try:
        os.makedirs(VAULT_PATH, exist_ok=True)
    except OSError as e:
        raise PlanError(f"Cannot create vault directory '{VAULT_PATH}': {e}")

    try:
        conn = get_connection()
        t = today()
        lines = []
        lines.append(f"# Plans — {t}\n")

        lines.append("## Daily Habits\n")
        habits = conn.execute("SELECT * FROM habits").fetchall()
        for habit in habits:
            history = conn.execute(
                "SELECT completed FROM habit_history WHERE habit_id = ? AND date = ?",
                (habit['id'], t)
            ).fetchone()
            checked = history and history['completed']
            box = "[x]" if checked else "[ ]"
            completed, total = get_checklist_progress(habit['id'], 'habit')
            progress = f" ({completed}/{total})" if total > 0 else ""
            lines.append(f"- {box} {habit['name']}{progress}\n")
        lines.append("\n")

        lines.append("## Today's Tasks\n")
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE project_id IS NULL AND status IN ('open', 'done')"
        ).fetchall()
        for task in tasks:
            completed, total = get_checklist_progress(task['id'], 'task')
            progress = f" ({completed}/{total})" if total > 0 else ""
            box = "[x]" if task['status'] == 'done' else "[ ]"
            lines.append(f"- {box} {task['name']}{progress}\n")
        lines.append("\n")

        lines.append("## Projects\n")
        projects = conn.execute("SELECT * FROM projects WHERE status = 'active'").fetchall()
        for project in projects:
            lines.append(f"### {project['name']}\n")
            project_tasks = conn.execute(
                "SELECT * FROM tasks WHERE project_id = ? AND status IN ('open', 'done')",
                (project['id'],)
            ).fetchall()
            for task in project_tasks:
                completed, total = get_checklist_progress(task['id'], 'task')
                progress = f" ({completed}/{total})" if total > 0 else ""
                box = "[x]" if task['status'] == 'done' else "[ ]"
                lines.append(f"- {box} {task['name']}{progress}\n")
            lines.append("\n")

        conn.close()
    except PlanError:
        raise
    except Exception as e:
        raise PlanError(f"Failed to read data for export: {e}")

    filepath = os.path.join(VAULT_PATH, "plans.md")
    try:
        with open(filepath, 'w') as f:
            f.writelines(lines)
    except OSError as e:
        raise PlanError(f"Cannot write to '{filepath}': {e}")

if __name__ == "__main__":
    export_to_obsidian()
