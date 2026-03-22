"""
logic/reset.py — Daily reset logic for Plans.

run_daily_reset() is called by setup_cron.sh every morning at 6:00 AM.
It does two things:
  1. Deletes tasks that were marked 'done' on a previous day (they're gone for good).
  2. Creates habit_history entries for today for every habit that is due today,
     so they appear on the dashboard as unchecked.
"""

from src.database import get_connection
from src.utils.date import today
from datetime import datetime

DAYS = {
    'mon': 0, 'tue': 1, 'wed': 2,
    'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6
}

def is_habit_due(repeat, today_str):
    """Return True if a habit's repeat schedule includes today.

    Supported formats: 'daily', 'weekly:mon,wed,fri', 'monthly:15', 'yearly:15-03'.
    """
    today_dt = datetime.strptime(today_str, "%d-%m-%Y")
    weekday = today_dt.weekday()
    day_of_month = today_dt.day
    month_day = today_dt.strftime("%d-%m")

    if repeat == 'daily':
        return True
    elif repeat.startswith('weekly:'):
        days = repeat.split(':')[1].split(',')
        return weekday in [DAYS[d.strip()] for d in days]
    elif repeat.startswith('monthly:'):
        return day_of_month == int(repeat.split(':')[1])
    elif repeat.startswith('yearly:'):
        return month_day == repeat.split(':')[1]
    return False

def run_daily_reset():
    """Delete completed tasks from previous days and seed today's habit_history rows."""
    conn = get_connection()
    t = today()

    # Permanently remove tasks that were completed on a previous day
    conn.execute("DELETE FROM tasks WHERE status = 'done' AND created < ?", (t,))
    conn.commit()

    habits = conn.execute("SELECT * FROM habits").fetchall()
    for habit in habits:
        if not is_habit_due(habit['repeat'], t):
            continue
        existing = conn.execute(
            "SELECT * FROM habit_history WHERE habit_id = ? AND date = ?",
            (habit['id'], t)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO habit_history (habit_id, date, completed) VALUES (?, ?, 0)",
                (habit['id'], t)
            )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_daily_reset()
    print("Daily reset complete.")
