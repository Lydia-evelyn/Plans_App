# Plans — Usage Guide

## What Plans is

Plans is a terminal-based productivity app (TUI) built with Python + Textual. It manages three things: **habits**, **tasks**, and **projects** — all stored locally in a SQLite database, with optional two-way sync to Obsidian via Markdown files.

---

## Launching the app

```bash
plans
```

This opens the dashboard. If you installed the shell wrapper correctly (see README), that's all you need. Otherwise, from inside the project directory:

```bash
python3 main.py
```

---

## The dashboard

The first screen you see. It shows:

- **ASCII header** — switches between "MORNING" and "EVENING" at 6 PM
- **Oreo** — a cat
- **Calendar** — current month, today highlighted in green
- **Habits panel** — each habit with ✓/○ state and a streak bar
- **Tasks panel** — today's standalone tasks with ✓/○ state

### Dashboard keys

| Key | Action |
|-----|--------|
| `H` | Go to Habits screen |
| `T` | Go to Tasks screen |
| `P` | Go to Projects screen |
| `E` | Export to Obsidian |
| `I` | Import from Obsidian |
| `R` | Refresh the dashboard |
| `Q` | Quit the app |

---

## Habits

Habits are recurring activities you track daily (or on a custom schedule). Each habit has a **streak counter** — consecutive days you've completed it.

### Opening the Habits screen

Press `H` from the dashboard. Press `ESC` to return.

### Adding a habit

Press `A`. You'll be asked for:
- **Name** — what the habit is
- **Repeat schedule** — how often it recurs (see formats below)

### Repeat schedule formats

| Format | Meaning |
|--------|---------|
| `daily` | Every day |
| `weekly:mon,wed,fri` | Every Monday, Wednesday, Friday |
| `monthly:15` | 15th of every month |
| `yearly:15-03` | Every 15th of March |

### Completing a habit

Navigate to it with the arrow keys and press `Enter` to toggle it complete/incomplete. The ✓ symbol appears when done. Your streak updates immediately.

### Streaks

A streak is the number of consecutive days you completed a habit (most recent first). It resets to 0 the first time you miss a day. The streak bar on the dashboard shows up to 10 days.

---

## Tasks

Tasks are one-off to-dos with an optional due date. They reset each morning — completed tasks from the previous day are removed by the daily cron job.

### Opening the Tasks screen

Press `T` from the dashboard. Press `ESC` to return.

### Adding a task

Press `A`. You'll be asked for:
- **Name** — what needs doing
- **Due date** — optional, in `DD-MM-YYYY` format (just press Enter to skip)

### Completing a task

Navigate to it and press `Enter`. Done tasks show with strikethrough text. They disappear the next morning.

---

## Projects

Projects are containers for multi-step tasks. A project can have as many tasks as you like and can be archived when done.

### Opening the Projects screen

Press `P` from the dashboard. Press `ESC` to return.

### Adding a project

Press `A`. You'll be asked for:
- **Name** — the project name
- **Header style** — visual style: `block`, `thin`, or `shadow` (controls how it looks when exported to Obsidian)

### Working inside a project

Select a project and press `Enter` to open it. Inside you can press `A` to add tasks to that project and `Enter` to complete them.

---

## Obsidian sync

Plans can export your data to a Markdown file in your Obsidian vault, and import changes back from it. This is the mobile workflow — check things off in Obsidian on your phone, then sync back when you're at your laptop.

### Setup

Add this to your `~/.zshrc`:

```bash
export PLANS_VAULT_PATH="/Users/yourname/path/to/your/ObsidianVault/Plans App"
```

Then run:

```bash
source ~/.zshrc
```

### Exporting

Press `E` on the dashboard. This writes `plans.md` to your vault, overwriting any previous export. The file uses standard Obsidian checkbox syntax:

```markdown
# Plans — 16-03-2026

## Daily Habits
- [x] Morning run
- [ ] Read

## Today's Tasks
- [ ] Buy groceries
- [x] Reply to emails

## Projects
### Website redesign
- [ ] Write copy for homepage
- [x] Finalize colour palette
```

### Importing

Press `I` on the dashboard. Plans reads your `plans.md` and:
- Marks habits as complete if they're checked `[x]`
- Creates new habits if you added lines that don't exist in Plans yet (defaults to `daily` repeat — you can change the schedule inside Plans afterwards)
- Marks tasks as done if they're checked `[x]`
- Creates new standalone tasks if you added unchecked lines

If any lines in the file don't match the expected format, you'll see a yellow warning toast for each one. Nothing is lost — unrecognised lines are skipped rather than causing an error.

### Automatic export on startup

The dashboard refreshes automatically every time you return to it, but export does not happen automatically. To automate export and import, see the cron setup in the README.

---

## Error messages

Any failure in the app surfaces as a notification toast in the bottom-right corner. Errors are red; warnings are yellow. Toasts stay visible for **15 seconds** and can be dismissed early by pressing `Enter`.

If you see a red error, the message will tell you exactly what failed and (where possible) how to fix it — e.g. "PLANS_VAULT_PATH is not set", "Cannot connect to database at '...'", "Project 'X' found in export file but does not exist in Plans."

---

## Daily reset

A cron job (`setup_cron.sh`) runs `plans-import` at 6:00 AM each morning. It:
1. Deletes tasks that were marked done the previous day
2. Seeds today's habit history entries (one unchecked row per habit that's due today)

To install it:

```bash
bash setup_cron.sh
```

---

## File structure

```
plans/
├── main.py                  # Entry point — initialises DB and launches app
├── plans                    # Shell wrapper (install to ~/.local/bin/)
├── plans-export             # Shell script: export only
├── plans-import             # Shell script: import only
├── setup_cron.sh            # Installs the 6AM cron job
├── TODO.txt                 # Shared task list (you + Claude both use this)
├── data/
│   └── plans.db             # SQLite database (all your data lives here)
└── src/
    ├── database.py          # DB connection + schema initialisation
    ├── config.py            # JSON config loader (~/.plans_config.json)
    ├── models/
    │   ├── habits.py        # Habit CRUD + toggle
    │   ├── tasks.py         # Task CRUD + complete/edit
    │   ├── projects.py      # Project CRUD + archive
    │   └── checklist.py     # Subtask CRUD (UI not yet wired)
    ├── logic/
    │   ├── streaks.py       # Streak calculation
    │   ├── export.py        # Export to Obsidian Markdown
    │   ├── import_md.py     # Import from Obsidian Markdown
    │   └── reset.py         # Daily reset logic
    ├── ui/
    │   ├── app.py           # PlansApp (root Textual app)
    │   ├── screens/
    │   │   ├── base.py      # BaseScreen + BaseAddScreen
    │   │   ├── dashboard.py # Dashboard + HabitsWidget + TasksWidget
    │   │   ├── habits.py    # HabitsScreen + AddHabitScreen
    │   │   ├── tasks.py     # TasksScreen + AddTaskScreen
    │   │   └── projects.py  # ProjectsScreen + ProjectTasksScreen + AddProjectScreen
    │   └── widgets/
    │       ├── header.py    # ASCII art logo
    │       ├── calendar.py  # Monthly calendar
    │       └── animal.py    # ASCII art cat (Oreo)
    └── utils/
        ├── date.py          # Date helpers (DD-MM-YYYY format throughout)
        └── errors.py        # PlanError exception class
```

---

## Data format notes

- All dates stored as `DD-MM-YYYY` strings (not ISO format). Don't sort them lexicographically — use `datetime.strptime` with `"%d-%m-%Y"`.
- Habits have a `repeat` field (see formats above). The daily reset checks this each morning to decide whether to seed a new history row.
- `checklist_items` rows exist in the DB and are shown as progress counts `(2/5)` on the dashboard — subtask UI is on the roadmap (see TODO.txt).
