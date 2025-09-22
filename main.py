from pathlib import Path
from ui import QuizUI
from quiz import QuizGame
from user import UserProfile
from scripts.init_db import init_database

DB_PATH = Path("data/app.db")

def main():
    # 1. Инициализация базы
    if not DB_PATH.exists():
        print("[INFO] Database not found, initializing...")
        init_database(DB_PATH)

    # 2. Создание основных объектов
    profile = UserProfile(DB_PATH)
    game = QuizGame(DB_PATH)
    ui = QuizUI()

    # 3. Гарантия наличия пользователя
    user_id = profile.ensure_default_user()

    # 4. Подготовка категорий для UI
    ui.set_categories(game.list_categories())

    # ====== Колбэки ======

    def on_start_game(category: str):
        game.start_game(category)
        q = game.get_next_question()
        if q:
            remaining_for_ui = game.get_remaining() + 1  # включаем текущий
            ui.show_question(q, remaining_for_ui, game.get_score(), 20)
        else:
            ui.show_result(game.get_score())

    def on_answer(question_id: int, index: int, time_spent_sec: int):
        is_correct = game.check_answer(question_id, index, time_spent_sec)
        print(f"[DEBUG] Answer: {'correct' if is_correct else 'wrong'}")
        q = game.get_next_question()
        if q:
            remaining_for_ui = game.get_remaining() + 1
            ui.show_question(q, remaining_for_ui, game.get_score(), 20)
        else:
            # сохраняем результат
            profile.save_result(user_id, game.get_score(), 20 * len(game.questions), q.category if q else "unknown")
            ui.show_result(game.get_score())

    def on_time_up(question_id: int, time_spent_sec: int):
        print(f"[DEBUG] Time is up for question {question_id}")
        # считаем как неправильный ответ
        q = game.get_next_question()
        if q:
            remaining_for_ui = game.get_remaining() + 1
            ui.show_question(q, remaining_for_ui, game.get_score(), 20)
        else:
            profile.save_result(user_id, game.get_score(), 20 * len(game.questions), q.category if q else "unknown")
            ui.show_result(game.get_score())

    def on_open_profile():
        try:
            print(f"[DEBUG] Loading profile for user_id: {user_id}")
            data = profile.load_profile(user_id)
            stats = profile.get_stats(user_id)
            print(f"[DEBUG] Profile loaded: {data}")
            ui.show_profile(data, stats)
        except Exception as e:
            print(f"[ERROR] Error loading profile: {e}")
            try:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Ошибка", f"Не удалось загрузить профиль: {str(e)}")
            except Exception:
                pass
            ui.show_main_menu()

    def on_update_profile(name, avatar_path):
        try:
            print(f"[DEBUG] Updating profile: name='{name}', avatar_path='{avatar_path}'")
            profile.update_profile(user_id, name, avatar_path)
            print("[DEBUG] Profile updated successfully")
            on_open_profile()
        except Exception as e:
            print(f"[ERROR] Error updating profile: {e}")
            try:
                # Показываем ошибку пользователю
                import tkinter.messagebox as messagebox
                messagebox.showerror("Ошибка", f"Не удалось обновить профиль: {str(e)}")
            except Exception as msg_error:
                print(f"[ERROR] Error showing message box: {msg_error}")
            # Возвращаемся к профилю без изменений
            try:
                on_open_profile()
            except Exception as profile_error:
                print(f"[ERROR] Error reopening profile: {profile_error}")
                ui.show_main_menu()

    def on_back_to_menu():
        ui.show_main_menu()

    # 5. Привязка колбэков
    ui.bind_actions(
        on_start_game,
        on_answer,
        on_time_up,
        on_open_profile,
        on_update_profile,
        on_back_to_menu
    )

    # 6. Запуск
    ui.show_main_menu()
    ui.mainloop()


if __name__ == "__main__":
    main()
