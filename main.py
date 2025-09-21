from pathlib import Path
from ui import QuizUI
from quiz import QuizGame
from user import UserProfile
from scripts.init_db import init_db


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"

def ensure_db():
    if not DB_PATH.exists():
        print("[INFO] Database not found, initializing...")
        init_db(DB_PATH)

def main():
    ensure_db()

    profile = UserProfile(DB_PATH)
    game = QuizGame(DB_PATH)
    ui = QuizUI()

    user_id = profile.ensure_default_user()

    # ========== Привязка колбэков ==========
    def on_start_game(category: str):
        game.start_game(category)
        q = game.get_next_question()
        if q:
            ui.show_question(q, game.get_remaining(), game.get_score(), 20)
        else:
            ui.show_result(game.get_score())

    def on_answer(index: int):
        # Заглушка: позже Армен добавит логику учета времени
        print(f"[DEBUG] Answer chosen: {index}")

    def on_time_up():
        print("[DEBUG] Time is up!")

    def on_open_profile():
        data = profile.load_profile(user_id)
        stats = profile.get_stats(user_id)
        ui.show_profile(data, stats)

    def on_update_profile(name, avatar_path):
        profile.update_profile(user_id, name, avatar_path)
        on_open_profile()

    def on_back_to_menu():
        ui.show_main_menu()

    ui.bind_actions(
        on_start_game,
        on_answer,
        on_time_up,
        on_open_profile,
        on_update_profile,
        on_back_to_menu
    )

    ui.show_main_menu()
    ui.mainloop()

if __name__ == "__main__":
    main()
