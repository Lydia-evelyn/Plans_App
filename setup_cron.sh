#!/usr/bin/env bash
# setup_cron.sh — installs the daily reset cron job
# Run once: bash setup_cron.sh

PLANS_DIR="$HOME/plans"
CRON_CMD="0 6 * * * cd $PLANS_DIR && python3 -c 'from src.database import initialize_db; from src.logic.reset import run_daily_reset; from src.logic.streaks import update_all_streaks; initialize_db(); run_daily_reset(); update_all_streaks()' >> $HOME/.plans_reset.log 2>&1"

# Check if already installed
if crontab -l 2>/dev/null | grep -q "plans"; then
    echo "Plans cron job already installed."
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "Cron job installed. Plans will reset habits daily at 6:00 AM."
fi

echo ""
echo "Current crontab:"
crontab -l
