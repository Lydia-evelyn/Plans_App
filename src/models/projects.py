"""
models/projects.py — CRUD operations for the projects table.

Projects are containers for tasks. Deleting a project also deletes its tasks.
Projects can be archived (hidden from active view) without being deleted.
"""

from src.database import get_connection
from src.utils.date import today
from src.utils.errors import PlanError


def get_all_projects(status='active'):
    """Return projects filtered by status ('active' or 'archived')."""
    try:
        conn = get_connection()
        projects = conn.execute(
            "SELECT * FROM projects WHERE status = ?", (status,)
        ).fetchall()
        conn.close()
        return projects
    except Exception as e:
        raise PlanError(f"Failed to load projects: {e}")

def add_project(name, header_style='block'):
    """Insert a new active project. header_style: 'block', 'thin', or 'shadow'."""
    if not name or not name.strip():
        raise PlanError("Project name cannot be empty.")
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO projects (name, header_style, created) VALUES (?, ?, ?)",
            (name, header_style, today())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to add project '{name}': {e}")

def archive_project(project_id):
    """Set a project's status to 'archived' so it's hidden from the active list."""
    try:
        conn = get_connection()
        conn.execute("UPDATE projects SET status = 'archived' WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to archive project {project_id}: {e}")

def delete_project(project_id):
    """Permanently delete a project and all of its tasks."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to delete project {project_id}: {e}")
