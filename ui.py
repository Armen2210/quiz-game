import tkinter as tk
from quiz import Question

class QuizUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Game")
        self.geometry("500x400")

    def bind_actions(self,
                     on_start_game,
                     on_answer,
                     on_time_up,
                     on_open_profile,
                     on_update_profile,
                     on_back_to_menu):
        self.on_start_game = on_start_game
        self.on_answer = on_answer
        self.on_time_up = on_time_up
        self.on_open_profile = on_open_profile
        self.on_update_profile = on_update_profile
        self.on_back_to_menu = on_back_to_menu

    def show_main_menu(self):
        print("[UI] Show main menu")

    def show_category_menu(self, categories):
        print("[UI] Show category menu")

    def show_question(self, question: Question, remaining: int, score: int, timer_sec: int):
        print(f"[UI] Question: {question.text}")

    def show_result(self, score: int):
        print(f"[UI] Result: {score}")

    def show_profile(self, profile_data: dict, stats: dict):
        print(f"[UI] Profile: {profile_data}, Stats: {stats}")
