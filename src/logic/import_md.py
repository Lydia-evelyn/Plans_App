"""
logic/import_md.py — Import completions and new items from an Obsidian Markdown file.

MERGE BEHAVIOUR:
  - Daily Habits: checked items are marked complete in habit_history.
    Unknown habit names are created with a default 'daily' repeat.
  - Today's Tasks / Projects: checked items are marked done.
    Unknown task names are created as new open tasks.
  - Inbox: all items are created as new tasks in the DB (unchecked → open,
    checked → done). After processing, the ## Inbox section is removed from
    the file so items don't get re-imported on the next run.

Vault path is read from the PLANS_VAULT_PATH environment variable.
"""

import os
import re
from src.database import get_connection
from src.utils.date import today
from src.utils.errors import PlanError

VAULT_PATH = os.path.expandvars(os.path.expanduser(
    os.environ.get('PLANS_VAULT_PATH', '~/Documents/ObsidianVault/plans')
))

KNOWN_SECTIONS = {"## Daily Habits", "## Today's Tasks", "## Projects", "## Inbox"}
CHECKBOX_RE = re.compile(r'^- \[( |x)\] ')


def _remove_inbox_from_file(filepath):
    """Rewrite plans.md with the ## Inbox section removed.

    Called after inbox items have been imported so they don't get re-imported.
    Non-fatal — if the rewrite fails, the inbox just persists until the next export.
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        filtered = []
        skip = False
        for line in lines:
            stripped = line.strip()
            if stripped == '## Inbox':
                skip = True
                continue
            if skip and stripped.startswith('## '):
                skip = False
            if not skip:
                filtered.append(line)

        # Clean up trailing blank lines
        while filtered and filtered[-1].strip() == '':
            filtered.pop()
        filtered.append('\n')

        with open(filepath, 'w') as f:
            f.writelines(filtered)
    except OSError:
        pass  # Non-fatal


def import_from_obsidian():
    """Parse plans.md and apply changes to the local database.

    Returns a list of warning strings for lines that were skipped or auto-created.
    Raises PlanError on hard failures (missing file, bad DB, unknown project).
    """
    if not VAULT_PATH:
        raise PlanError("PLANS_VAULT_PATH is not set. Add it to your ~/.zshrc and run 'source ~/.zshrc'.")

    filepath = os.path.join(VAULT_PATH, "plans.md")

    if not os.path.exists(filepath):
        raise PlanError(f"No export file found at '{filepath}'. Run export first.")

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except OSError as e:
        raise PlanError(f"Cannot read '{filepath}': {e}")

    try:
        conn = get_connection()
        t = today()
        current_section = None
        current_project_id = None
        warnings = []
        inbox_imported = False

        for lineno, raw in enumerate(lines, start=1):
            line = raw.strip()

            # skip blank lines and the top-level title
            if not line or line.startswith("# "):
                continue

            # section headers
            if line in KNOWN_SECTIONS:
                current_section = {
                    "## Daily Habits": 'habits',
                    "## Today's Tasks": 'tasks',
                    "## Projects": 'projects',
                    "## Inbox": 'inbox',
                }[line]
                current_project_id = None
                continue

            # unknown ## header
            if line.startswith("## "):
                warnings.append(f"Line {lineno}: Unrecognised section '{line}' — skipped.")
                current_section = None
                current_project_id = None
                continue

            # project sub-header
            if line.startswith("### "):
                if current_section != 'projects':
                    warnings.append(f"Line {lineno}: Sub-header '{line}' outside Projects section — skipped.")
                    continue
                project_name = line[4:].strip()
                project = conn.execute(
                    "SELECT id FROM projects WHERE name = ?", (project_name,)
                ).fetchone()
                if project is None:
                    raise PlanError(f"Project '{project_name}' found in export file but does not exist in Plans.")
                current_project_id = project['id']
                continue

            # checkbox lines
            if CHECKBOX_RE.match(line):
                if current_section is None:
                    warnings.append(f"Line {lineno}: Checkbox item outside any section — skipped: '{line}'")
                    continue
                checked = line[3] == 'x'
                name = re.sub(r'\s*\(\d+/\d+\)$', '', line[6:].strip())
                if not name:
                    warnings.append(f"Line {lineno}: Checkbox item has no name — skipped.")
                    continue

                if current_section == 'habits':
                    habit = conn.execute(
                        "SELECT id FROM habits WHERE name = ?", (name,)
                    ).fetchone()
                    if habit is None:
                        conn.execute(
                            "INSERT INTO habits (name, repeat, streak, last_completed, created) VALUES (?, 'daily', 0, NULL, ?)",
                            (name, t)
                        )
                        habit = conn.execute("SELECT id FROM habits WHERE name = ?", (name,)).fetchone()
                        warnings.append(f"New habit '{name}' created from Obsidian (repeat defaults to 'daily').")

                    if checked:
                        existing = conn.execute(
                            "SELECT * FROM habit_history WHERE habit_id = ? AND date = ?",
                            (habit['id'], t)
                        ).fetchone()
                        if existing:
                            conn.execute(
                                "UPDATE habit_history SET completed = 1 WHERE habit_id = ? AND date = ?",
                                (habit['id'], t)
                            )
                        else:
                            conn.execute(
                                "INSERT INTO habit_history (habit_id, date, completed) VALUES (?, ?, 1)",
                                (habit['id'], t)
                            )
                        conn.execute(
                            "UPDATE habits SET last_completed = ? WHERE id = ?", (t, habit['id'])
                        )

                elif current_section in ('tasks', 'projects'):
                    if current_project_id:
                        task = conn.execute(
                            "SELECT id, status FROM tasks WHERE name = ? AND project_id = ?",
                            (name, current_project_id)
                        ).fetchone()
                    else:
                        task = conn.execute(
                            "SELECT id, status FROM tasks WHERE name = ? AND project_id IS NULL",
                            (name,)
                        ).fetchone()

                    if checked:
                        if task and task['status'] == 'open':
                            conn.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task['id'],))
                        elif not task:
                            warnings.append(f"Line {lineno}: Checked task '{name}' not found in Plans — skipped.")
                    else:
                        if not task:
                            conn.execute(
                                "INSERT INTO tasks (name, project_id, due, notify_before_days, status, created) "
                                "VALUES (?, ?, NULL, NULL, 'open', ?)",
                                (name, current_project_id, t)
                            )

                elif current_section == 'inbox':
                    # Inbox items are always new — create them as tasks
                    existing = conn.execute(
                        "SELECT id FROM tasks WHERE name = ? AND project_id IS NULL",
                        (name,)
                    ).fetchone()
                    if not existing:
                        status = 'done' if checked else 'open'
                        conn.execute(
                            "INSERT INTO tasks (name, project_id, due, notify_before_days, status, created) "
                            "VALUES (?, NULL, NULL, NULL, ?, ?)",
                            (name, status, t)
                        )
                        warnings.append(f"Inbox: new task '{name}' added to Plans.")
                    inbox_imported = True
                continue

            # anything else that isn't blank/comment — flag it
            if current_section is not None:
                warnings.append(f"Line {lineno}: Unrecognised format — skipped: '{line[:60]}'")

        conn.commit()
        conn.close()

        # Remove the inbox section now that items are in the DB
        if inbox_imported:
            _remove_inbox_from_file(filepath)

        return warnings
    except PlanError:
        raise
    except Exception as e:
        raise PlanError(f"Failed to parse or apply import from '{filepath}': {e}")


if __name__ == "__main__":
    import_from_obsidian()
