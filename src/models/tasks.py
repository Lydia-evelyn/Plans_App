"""
models/tasks.py — CRUD operations for tasks.

Tasks can be standalone (project_id=None) or attached to a project.
Open tasks are listed before done tasks; done tasks stay visible until
the daily reset removes them.
"""

from src.database import get_connection
from src.utils.date import today
from src.utils.errors import PlanError


def get_all_tasks(project_id=None):
    """Return all tasks, open first. Pass project_id to filter to a single project."""
    try:
        conn = get_connection()
        if project_id:
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE project_id = ? AND status IN ('open', 'done')"
                " ORDER BY CASE status WHEN 'open' THEN 0 ELSE 1 END, id",
                (project_id,)
            ).fetchall()
        else:
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE project_id IS NULL AND status IN ('open', 'done')"
                " ORDER BY CASE status WHEN 'open' THEN 0 ELSE 1 END, id"
            ).fetchall()
        conn.close()
        return tasks
    except Exception as e:
        raise PlanError(f"Failed to load tasks: {e}")

def add_task(name, project_id=None, due=None, notify_before_days=None):
    """Insert a new open task. due is a DD-MM-YYYY string or None."""
    if not name or not name.strip():
        raise PlanError("Task name cannot be empty.")
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO tasks (name, project_id, due, notify_before_days, status, created) VALUES (?, ?, ?, ?, 'open', ?)",
            (name, project_id, due, notify_before_days, today())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to add task '{name}': {e}")

def complete_task(task_id):
    """Mark a task as done. The daily reset will remove it the following morning."""
    try:
        conn = get_connection()
        conn.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to complete task {task_id}: {e}")

def delete_task(task_id):
    """Permanently delete a task by id."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to delete task {task_id}: {e}")

def edit_task(task_id, name=None, due=None, notify_before_days=None):
    """Update one or more fields on an existing task. Pass only the fields to change."""
    try:
        conn = get_connection()
        if name:
            conn.execute("UPDATE tasks SET name = ? WHERE id = ?", (name, task_id))
        if due:
            conn.execute("UPDATE tasks SET due = ? WHERE id = ?", (due, task_id))
        if notify_before_days:
            conn.execute("UPDATE tasks SET notify_before_days = ? WHERE id = ?", (notify_before_days, task_id))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to edit task {task_id}: {e}")
