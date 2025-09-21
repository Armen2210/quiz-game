from pathlib import Path
from typing import Optional
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
    categories = game.list_categories() #Антон: добавил строку # Метод Сергея
    print(f"[DEBUG] Loaded categories: {categories}")  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
    ui.set_categories(categories) #Антон: добавил строку
    current_question = None #Антон: добавил строку



    # ========== Привязка колбэков ==========
    def on_start_game(category: str):
        nonlocal current_question  # Антон: добавил строку (Разрешаем доступ к внешней переменной)
        game.start_game(category)
        q = game.get_next_question()
        if q:
            current_question = q #Антон: добавил строку
            ui.show_question(q, game.get_remaining(), game.get_score(), 20)
        else:
            ui.show_result(game.get_score())

    def on_answer(index: int, time_spent_sec: int): #Антон: добавли параметр "time_spent_sec: int"
        nonlocal current_question # Антон: Строку добавил
        if current_question: # Антон: Строку добавил
            is_correct = game.check_answer(current_question.id, index, time_spent_sec) # Антон: Строку добавил
            print(f"Ответ {'правильный' if is_correct else 'неправильный'}")# Антон: Строку добавил
            # Получаем следующий вопрос # Антон: Строку добавил
            next_q = game.get_next_question() # Антон: Строку добавил
            if next_q: # Антон: Строку добавил
                current_question = next_q # Антон: Строку добавил
                ui.show_question(next_q, game.get_remaining(), game.get_score(), 20) # Антон: Строку добавил
            else: # Антон: Строку добавил
                profile.save_result(user_id, game.get_score(), 0, current_question.category) # Антон: Строку добавил
                ui.show_result(game.get_score()) # Антон: Строку добавил
        else: # Антон: Строку добавил
            print("Ошибка: нет текущего вопроса!") # Антон: Строку добавил

        # Заглушка: позже Армен добавит логику учета времени
        #print(f"[DEBUG] Answer chosen: {index}") # Антон: Строку закоментировал


    def on_time_up(time_spent_sec: int):  # Антон: добавил параметры "time_spent_sec: int"
        # print("[DEBUG] Time is up!") # Антон: Строку закоментировал
        nonlocal current_question # Антон: Строку добавил
        if current_question: # Антон: Строку добавил
            # Сохраняем результат с временем
            profile.save_result(user_id, game.get_score(), time_spent_sec, current_question.category) # Антон: Строку добавил
        ui.show_result(game.get_score()) # Антон: Строку добавил

    def on_open_profile():
        data = profile.load_profile(user_id)
        stats = profile.get_stats(user_id)
        ui.show_profile(data, stats)

    def on_update_profile(name: str, avatar_path: Optional[str]):
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
