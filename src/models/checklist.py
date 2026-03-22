"""
models/checklist.py — CRUD for checklist_items (subtasks).

checklist_items can be attached to either a habit or a task.
parent_type is the string 'habit' or 'task'.
Items are ordered by the 'ordering' column (auto-incremented on add).
"""

from src.database import get_connection
from src.utils.errors import PlanError


def get_checklist(parent_id, parent_type):
    """Return all checklist items for a parent, sorted by ordering."""
    try:
        conn = get_connection()
        items = conn.execute(
            "SELECT * FROM checklist_items WHERE parent_id = ? AND parent_type = ? ORDER BY ordering",
            (parent_id, parent_type)
        ).fetchall()
        conn.close()
        return items
    except Exception as e:
        raise PlanError(f"Failed to load checklist for {parent_type} {parent_id}: {e}")

def add_checklist_item(parent_id, parent_type, name):
    """Append a new incomplete checklist item, placed after all existing items."""
    if not name or not name.strip():
        raise PlanError("Checklist item name cannot be empty.")
    try:
        conn = get_connection()
        max_order = conn.execute(
            "SELECT MAX(ordering) FROM checklist_items WHERE parent_id = ? AND parent_type = ?",
            (parent_id, parent_type)
        ).fetchone()[0] or 0
        conn.execute(
            "INSERT INTO checklist_items (parent_id, parent_type, name, completed, ordering) VALUES (?, ?, ?, 0, ?)",
            (parent_id, parent_type, name, max_order + 1)
        )
        conn.commit()
        conn.close()
    except PlanError:
        raise
    except Exception as e:
        raise PlanError(f"Failed to add checklist item '{name}': {e}")

def toggle_checklist_item(item_id):
    """Flip the completed state of a checklist item (0→1 or 1→0)."""
    try:
        conn = get_connection()
        current = conn.execute(
            "SELECT completed FROM checklist_items WHERE id = ?", (item_id,)
        ).fetchone()
        if current is None:
            raise PlanError(f"Checklist item {item_id} not found.")
        new_val = 0 if current['completed'] else 1
        conn.execute("UPDATE checklist_items SET completed = ? WHERE id = ?", (new_val, item_id))
        conn.commit()
        conn.close()
    except PlanError:
        raise
    except Exception as e:
        raise PlanError(f"Failed to toggle checklist item {item_id}: {e}")

def complete_checklist_item(item_id):
    """Mark a checklist item as completed (one-way — use toggle to undo)."""
    try:
        conn = get_connection()
        conn.execute("UPDATE checklist_items SET completed = 1 WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to complete checklist item {item_id}: {e}")

def delete_checklist_item(item_id):
    """Permanently remove a checklist item."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM checklist_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to delete checklist item {item_id}: {e}")

def get_checklist_progress(parent_id, parent_type):
    """Return (completed_count, total_count) for a parent's checklist."""
    try:
        conn = get_connection()
        total = conn.execute(
            "SELECT COUNT(*) FROM checklist_items WHERE parent_id = ? AND parent_type = ?",
            (parent_id, parent_type)
        ).fetchone()[0]
        completed = conn.execute(
            "SELECT COUNT(*) FROM checklist_items WHERE parent_id = ? AND parent_type = ? AND completed = 1",
            (parent_id, parent_type)
        ).fetchone()[0]
        conn.close()
        return completed, total
    except Exception as e:
        raise PlanError(f"Failed to get checklist progress for {parent_type} {parent_id}: {e}")
