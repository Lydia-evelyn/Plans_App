"""
database.py — Central SQLite access layer for Plans.

All other modules call get_connection() from here.
Schema: habits, habit_history, projects, tasks, checklist_items.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'plans.db')


def get_connection():
    """Open a connection to plans.db with row_factory=sqlite3.Row.

    Raises RuntimeError if the DB file cannot be opened.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(
            f"Cannot connect to database at '{DB_PATH}': {e}\n"
            f"Make sure the 'data/' directory exists and is writable."
        )

def initialize_db():
    """Create all tables if they don't already exist. Safe to call on every startup."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            repeat TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_completed TEXT,
            created TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS habit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            header_style TEXT DEFAULT 'block',
            created TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER,
            due TEXT,
            notify_before_days INTEGER,
            status TEXT DEFAULT 'open',
            created TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER NOT NULL,
            parent_type TEXT NOT NULL,
            name TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            ordering INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_habit_history_habit_date
            ON habit_history(habit_id, date);
    """)
    try:
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to initialize database schema: {e}")

if __name__ == "__main__":
    initialize_db()
    print("Database initialized.")
