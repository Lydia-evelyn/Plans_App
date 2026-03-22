"""
logic/streaks.py — Streak calculation for habits.

Dates are stored as DD-MM-YYYY strings throughout the app.

Streak logic: walk backwards from today one day at a time. For each day,
check if the habit was due. If due and completed — increment streak. If due
and not completed — break. If not due — skip. This correctly handles gaps
caused by weekly/monthly schedules and missed cron runs.
"""

from datetime import datetime, timedelta
from src.database import get_connection
from src.utils.errors import PlanError
from src.utils.date import today, parse, DATE_FORMAT


def _is_habit_due(repeat, date_str):
    """Return True if a habit's repeat schedule includes the given date.

    Supported formats: 'daily', 'weekly:mon,wed,fri', 'monthly:15', 'yearly:15-03'.
    """
    DAYS = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
    dt = parse(date_str)
    if repeat == 'daily':
        return True
    elif repeat.startswith('weekly:'):
        days = repeat.split(':')[1].split(',')
        return dt.weekday() in [DAYS[d.strip()] for d in days]
    elif repeat.startswith('monthly:'):
        return dt.day == int(repeat.split(':')[1])
    elif repeat.startswith('yearly:'):
        return dt.strftime("%d-%m") == repeat.split(':')[1]
    return False


def calculate_streak(habit_id):
    """Count consecutive completed due-days for a habit, walking backwards from today.

    Skips days the habit wasn't scheduled. Breaks as soon as a due day is
    found with no completion. Returns 0 if the habit has never been completed
    or if today's due entry is not yet completed.

    Raises PlanError if the DB query fails.
    """
    try:
        conn = get_connection()
        habit = conn.execute(
            "SELECT repeat FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        history_rows = conn.execute(
            "SELECT date, completed FROM habit_history WHERE habit_id = ?",
            (habit_id,)
        ).fetchall()
        conn.close()
    except Exception as e:
        raise PlanError(f"Failed to fetch habit history for habit {habit_id}: {e}")

    if not habit:
        return 0

    # Build a quick lookup: date string → completed (0 or 1)
    history_map = {row['date']: row['completed'] for row in history_rows}

    repeat = habit['repeat']
    today_dt = parse(today())
    streak = 0

    for i in range(365):
        check_dt = today_dt - timedelta(days=i)
        check_str = check_dt.strftime(DATE_FORMAT)

        if not _is_habit_due(repeat, check_str):
            continue  # not a scheduled day — skip without breaking streak

        if history_map.get(check_str) == 1:
            streak += 1
        else:
            break  # due day with no completion — streak is over

    return streak

def update_all_streaks():
    """Recalculate and persist streaks for every habit. Used at startup and by cron."""
    try:
        conn = get_connection()
        habits = conn.execute("SELECT * FROM habits").fetchall()
        for habit in habits:
            streak = calculate_streak(habit['id'])
            conn.execute("UPDATE habits SET streak = ? WHERE id = ?", (streak, habit['id']))
        conn.commit()
        conn.close()
    except PlanError:
        raise
    except Exception as e:
        raise PlanError(f"Failed to update streaks: {e}")

if __name__ == "__main__":
    update_all_streaks()
    print("Streaks updated.")
