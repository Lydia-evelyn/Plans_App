"""
models/habits.py — CRUD and toggle operations for habits.

Raises PlanError on all failures so the UI can display a consistent
error notification without catching raw sqlite3/OS exceptions.
"""

from src.database import get_connection
from src.utils.date import today
from src.utils.errors import PlanError
from src.logic.streaks import calculate_streak


def get_all_habits():
    """Return all habits ordered by insertion (id). Raises PlanError on DB failure."""
    try:
        conn = get_connection()
        habits = conn.execute("SELECT * FROM habits").fetchall()
        conn.close()
        return habits
    except Exception as e:
        raise PlanError(f"Failed to load habits: {e}")

def add_habit(name, repeat):
    """Insert a new habit. repeat format: 'daily', 'weekly:mon,wed', 'monthly:15', 'yearly:15-03'."""
    if not name or not name.strip():
        raise PlanError("Habit name cannot be empty.")
    if not repeat or not repeat.strip():
        raise PlanError("Repeat schedule cannot be empty.")
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO habits (name, repeat, created) VALUES (?, ?, ?)",
            (name, repeat, today())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to add habit '{name}': {e}")

def delete_habit(habit_id):
    """Delete a habit and all its history rows."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        conn.execute("DELETE FROM habit_history WHERE habit_id = ?", (habit_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to delete habit {habit_id}: {e}")

def toggle_habit(habit_id):
    """Toggle today's completion state for a habit, then recalculate and persist the streak."""
    try:
        conn = get_connection()
        t = today()
        existing = conn.execute(
            "SELECT * FROM habit_history WHERE habit_id = ? AND date = ?",
            (habit_id, t)
        ).fetchone()
        if existing:
            new_val = 0 if existing['completed'] else 1
            conn.execute(
                "UPDATE habit_history SET completed = ? WHERE habit_id = ? AND date = ?",
                (new_val, habit_id, t)
            )
            if new_val == 1:
                conn.execute("UPDATE habits SET last_completed = ? WHERE id = ?", (t, habit_id))
        else:
            conn.execute(
                "INSERT INTO habit_history (habit_id, date, completed) VALUES (?, ?, 1)",
                (habit_id, t)
            )
            conn.execute("UPDATE habits SET last_completed = ? WHERE id = ?", (t, habit_id))
        conn.commit()  # commit history change first so calculate_streak sees it
        streak = calculate_streak(habit_id)
        conn.execute("UPDATE habits SET streak = ? WHERE id = ?", (streak, habit_id))
        conn.commit()
        conn.close()
    except PlanError:
        raise
    except Exception as e:
        raise PlanError(f"Failed to toggle habit {habit_id}: {e}")

def complete_habit(habit_id):
    """Mark today's entry for a habit as completed (idempotent — won't double-count)."""
    try:
        conn = get_connection()
        t = today()
        existing = conn.execute(
            "SELECT * FROM habit_history WHERE habit_id = ? AND date = ?",
            (habit_id, t)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE habit_history SET completed = 1 WHERE habit_id = ? AND date = ?",
                (habit_id, t)
            )
        else:
            conn.execute(
                "INSERT INTO habit_history (habit_id, date, completed) VALUES (?, ?, 1)",
                (habit_id, t)
            )
        conn.execute("UPDATE habits SET last_completed = ? WHERE id = ?", (t, habit_id))
        conn.commit()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to complete habit {habit_id}: {e}")
