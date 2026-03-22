from src.database import initialize_db
from src.logic.reset import run_daily_reset
from src.logic.streaks import update_all_streaks
from src.ui.app import PlansApp

if __name__ == "__main__":
    initialize_db()
    run_daily_reset()
    update_all_streaks()
    app = PlansApp()
    app.run()
