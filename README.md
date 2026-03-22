# Plans

Your personal productivity TUI. Habits, tasks, projects — owned by you, lives in your terminal.

## Setup

### 1. Install dependencies
```bash
pip install textual rich
```

### 2. Make the shell commands executable
```bash
chmod +x plans plans-export plans-import setup_cron.sh
```

### 3. Install shell commands globally
```bash
cp plans ~/.local/bin/plans
cp plans-export ~/.local/bin/plans-export
cp plans-import ~/.local/bin/plans-import
```

Make sure `~/.local/bin` is in your PATH. Add this to your `~/.zshrc` or `~/.bashrc` if needed:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 4. Set your Obsidian vault path
```bash
export PLANS_VAULT_PATH="$HOME/path/to/your/ObsidianVault/plans"
```
Add this to your `~/.zshrc` or `~/.bashrc` to make it permanent.

### 5. Install the daily reset cron job
```bash
bash setup_cron.sh
```
This runs the habit reset every morning at 6:00 AM.

## Usage

```bash
plans              # launch the TUI dashboard
plans-export       # export today's checklist to Obsidian
plans-import       # sync checked items back from Obsidian
```

## Inside the TUI

| Key | Action |
|-----|--------|
| H | Habits screen |
| T | Tasks screen |
| P | Projects screen |
| E | Export to Obsidian |
| I | Import from Obsidian |
| Q | Quit |

## Repeat schedule format

| Format | Meaning |
|--------|---------|
| `daily` | Every day |
| `weekly:mon,wed,fri` | Every Monday, Wednesday, Friday |
| `monthly:15` | 15th of every month |
| `yearly:15-03` | Every 15th of March |

## Obsidian sync flow

1. Run `plans` in the morning — dashboard auto-exports to your vault
2. Check off tasks in Obsidian on mobile throughout the day
3. Run `plans-import` when back at your laptop to sync completions
