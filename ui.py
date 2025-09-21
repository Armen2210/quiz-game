import tkinter as tk
from quiz import Question
from typing import List, Optional, Dict, Any, Callable

class QuizUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Game")
        self.geometry("500x500")
        self.timer_id = None
        self.total_seconds = 0
        self._categories: List[str] = []

    def _disable_options(self):
        """Отключает все кнопки вариантов ответов"""
        if hasattr(self, 'option_buttons'):
            for btn in self.option_buttons:
                btn.config(state=tk.DISABLED)
        self._cancel_timer_if_any()

    def _on_answer_click(self, idx: int):
        """Обработчик клика по варианту ответа"""
        spent = int(self.total_seconds - self.current_time)  # Вычисляем время
        self._disable_options()  # Отключаем кнопки и таймер
        self.on_answer(idx, spent)  # Вызываем колбэк с временем

    def _cancel_timer_if_any(self):
        """Отменяет таймер если он активен"""
        if hasattr(self, 'timer_id') and self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def _tick(self):
        """Обновление таймера каждую секунду"""
        if self.current_time > 0 and hasattr(self, "timer_label"):
            self.timer_label.config(text=f"⏰ {self.current_time} сек")
            self.current_time -= 1
            self.timer_id = self.after(1000, self._tick)  # ← Планируем следующий tick
        else:
            # Время вышло
            self._disable_options()
            self.on_time_up(int(self.total_seconds))  # ← Передаем общее время

    def _cancel_timer_if_any(self):
        """Отменяет таймер если он активен"""
        if getattr(self, "timer_id", None) is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None


    def bind_actions(self,
                     on_start_game: Callable[[str], None],
                     on_answer: Callable[[int, int], None],
                     on_time_up: Callable[[int], None],
                     on_open_profile: Callable[[], None],
                     on_update_profile: Callable[[str, Optional[str]], None],
                     on_back_to_menu: Callable[[], None]
                     ) -> None:
        self.on_start_game = on_start_game
        self.on_answer = on_answer
        self.on_time_up = on_time_up
        self.on_open_profile = on_open_profile
        self.on_update_profile = on_update_profile
        self.on_back_to_menu = on_back_to_menu

    def set_categories(self, categories: List[str]) -> None:
        """Устанавливает список доступных категорий"""
        self._categories = categories or []
        print(f"[UI] Categories set: {self._categories}")  # Для отладки

    def show_main_menu(self):
        self._cancel_timer_if_any()
        # Очищаем окно от предыдущих виджетов
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем виджеты главного меню
        title_label = tk.Label(self, text="Викторина", font=("Arial", 24))
        title_label.pack(pady=50)

        start_button = tk.Button(self, text="Начать игру", command=lambda: self.show_category_menu(self._categories),
                                 width=20, height=2)
        start_button.pack(pady=10)

        profile_button = tk.Button(self, text="Профиль", command=self.on_open_profile, width=20, height=2)
        profile_button.pack(pady=10)

        exit_button = tk.Button(self, text="Выход", command=self.destroy, width=20, height=2)
        exit_button.pack(pady=10)


    def show_category_menu(self, categories):
        print(f"[UI] Showing category menu with: {categories}")
        self._cancel_timer_if_any()
        """
        Отображает меню выбора категории с кнопками для каждой категории

        Args:
            categories: Список уникальных категорий из CSV-файла
        """
        # Очищаем окно от предыдущих виджетов
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем основной фрейм с прокруткой (на случай многих категорий)
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        title_label = tk.Label(main_frame, text="Выберите категорию",
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        # Разделитель
        tk.Frame(main_frame, height=2, bg="gray").pack(fill=tk.X, pady=10)

        # Фрейм для кнопок категорий
        categories_frame = tk.Frame(main_frame)
        categories_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Создаем кнопки для каждой категории
        for category in categories:
            # Определяем русское название для категории
            category_names = {
                "history": "История",
                "science": "Наука",
                "culture": "Культура",
                "sport": "Спорт"
            }

            display_name = category_names.get(category, category.capitalize())

            # Создаем кнопку категории
            category_btn = tk.Button(self,
                                     text=display_name,
                                     command=lambda c=category: self.on_start_game(c),
                                     width=25,
                                     height=2,
                                     font=("Arial", 12),
                                     bg="#f0f0f0",
                                     relief=tk.RAISED)
            category_btn.pack(pady=8)

        # Кнопка возврата в главное меню
        back_button = tk.Button(main_frame,
                                text="← Назад в меню",
                                command=self.on_back_to_menu,
                                width=15,
                                height=1,
                                font=("Arial", 10),
                                bg="#e0e0e0")
        back_button.pack(pady=20)

    def show_question(self, question: Question, remaining: int, score: int, timer_sec: int):
        """
            Отображает экран с вопросом и вариантами ответов

            Args:
                question: Объект Question с данными вопроса
                remaining: Количество оставшихся вопросов
                score: Текущий счет
                timer_sec: Время на ответ в секундах
            """
        # Очищаем окно от предыдущих виджетов
        self._cancel_timer_if_any()
        for widget in self.winfo_children():
            widget.destroy()

        # Сохраняем общее время на вопрос
        self.total_seconds = int(timer_sec)  # ← Добавить
        self.current_time = int(timer_sec)

        # Основной фрейм
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Верхняя панель: счет и оставшиеся вопросы
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(top_frame, text=f"Счет: {score}",
                 font=("Arial", 12, "bold"), fg="green").pack(side=tk.LEFT)

        tk.Label(top_frame, text=f"Осталось вопросов: {remaining}",
                 font=("Arial", 12), fg="blue").pack(side=tk.RIGHT)

        # Таймер
        self.timer_label = tk.Label(main_frame, text=f"⏰ {timer_sec} сек",
                                    font=("Arial", 14, "bold"), fg="red")
        self.timer_label.pack(pady=(0, 10))

        # Запускаем обновление таймера
        self.current_time = timer_sec
        self.update_timer()

        # Текст вопроса
        question_frame = tk.Frame(main_frame)
        question_frame.pack(fill=tk.X, pady=20)

        question_label = tk.Label(question_frame, text=question.text,
                                  font=("Arial", 14),
                                  wraplength=450,
                                  justify=tk.CENTER)
        question_label.pack()

        # Фрейм для вариантов ответов
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        # Создаем кнопки вариантов ответов
        self.option_buttons = []

        for i, opt in enumerate(question.options):
            btn = tk.Button(options_frame,
                            text=option,
                            command=lambda idx=i: self.on_answer_click(idx),
                            width=40,
                            height=2,
                            font=("Arial", 11),
                            bg="#e8f4f8",
                            relief=tk.RAISED,
                            wraplength=400)
            btn.pack(pady=8)
            self.option_buttons.append(btn)

        # Кнопка выхода (на случай, если пользователь хочет прервать игру)
        exit_button = tk.Button(main_frame,
                                text="Выход в меню",
                                command=self.on_back_to_menu,
                                width=15,
                                height=1,
                                font=("Arial", 10),
                                bg="#ffcccc")
        exit_button.pack(pady=10)
        self.timer_id = self.after(1000, self._tick)  # ← Запуск таймера

    def update_timer(self):
        """Обновляет отображение таймера каждую секунду"""
        if hasattr(self, 'current_time') and self.current_time > 0:
            self.timer_label.config(text=f"⏰ {self.current_time} сек")
            self.current_time -= 1
            # Планируем следующее обновление через 1000 мс (1 секунду)
            self.timer_id = self.after(1000, self.update_timer)
        else:
            # Время вышло
            self.timer_label.config(text="⏰ Время вышло!", fg="red")
            self._disable_options()  # Отключаем кнопки
            self.on_time_up(0)  #  time_spent_sec = 0 (не успел ответить)

    def stop_timer(self):
        """Останавливает таймер, если он активен"""
        self._cancel_timer_if_any()  # ← Используем новый метод

    def show_result(self, score: int):
        """Показывает экран с результатами игры"""
        self._cancel_timer_if_any()

        # Очищаем окно
        for widget in self.winfo_children():
            widget.destroy()

        # Основной фрейм
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        title_label = tk.Label(main_frame, text="Результаты викторины",
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        # Разделитель
        tk.Frame(main_frame, height=2, bg="gray").pack(fill=tk.X, pady=10)

        # Счет
        score_frame = tk.Frame(main_frame)
        score_frame.pack(pady=30)

        tk.Label(score_frame, text="Ваш счет:",
                 font=("Arial", 16)).pack()

        tk.Label(score_frame, text=str(score),
                 font=("Arial", 24, "bold"),
                 fg="green").pack(pady=10)

        # Кнопки действий
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=30)

        # Кнопка "В меню"
        menu_button = tk.Button(buttons_frame,
                                text="В меню",
                                command=self.on_back_to_menu,
                                width=15,
                                height=2,
                                font=("Arial", 12),
                                bg="#e0e0e0")
        menu_button.pack(pady=10)

        # Кнопка "Профиль"
        profile_button = tk.Button(buttons_frame,
                                   text="Профиль",
                                   command=self.on_open_profile,
                                   width=15,
                                   height=2,
                                   font=("Arial", 12),
                                   bg="#e0e0e0")
        profile_button.pack(pady=10)

        # Опционально: Кнопка "Выбор категории"
        if hasattr(self, '_categories') and self._categories:
            category_button = tk.Button(buttons_frame,
                                        text="Выбор категории",
                                        command=lambda: self.show_category_menu(self._categories),
                                        width=15,
                                        height=2,
                                        font=("Arial", 12),
                                        bg="#e0e0e0")
            category_button.pack(pady=10)

    def show_profile(self, profile_data: dict, stats: dict):
        self._cancel_timer_if_any()
        # print(f"[UI] Profile: {profile_data}, Stats: {stats}")
        # Очищаем окно от предыдущих виджетов
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем основной контейнер с прокруткой
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        title_label = tk.Label(main_frame, text="Профиль игрока",
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        # Разделитель
        tk.Frame(main_frame, height=2, bg="gray").pack(fill=tk.X, pady=10)

        # Информация о пользователе
        user_frame = tk.Frame(main_frame)
        user_frame.pack(fill=tk.X, pady=10)

        tk.Label(user_frame, text="Имя:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(user_frame, text=profile_data.get("name", "Не указано"),
                 font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=(10, 0))

        tk.Label(user_frame, text="Уровень:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", pady=(5, 0))
        tk.Label(user_frame, text=profile_data.get("level", "Новичок"),
                 font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(5, 0))

        # Статистика
        stats_frame = tk.LabelFrame(main_frame, text="Статистика", font=("Arial", 14, "bold"))
        stats_frame.pack(fill=tk.X, pady=20)

        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(padx=10, pady=10)

        # Динамическое создание статистики
        stat_rows = [
            ("Всего игр", stats.get("total_games", 0)),
            ("Лучший счет", stats.get("best_score", 0)),
            ("Средний счет", stats.get("average_score", 0)),
            ("Правильные ответы", f"{stats.get('correct_answers', 0)}%"),
            ("Любимая категория", stats.get("favorite_category", "Не определена"))
        ]

        for i, (label, value) in enumerate(stat_rows):
            tk.Label(stats_grid, text=label + ":", font=("Arial", 11, "bold")).grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(stats_grid, text=str(value), font=("Arial", 11)).grid(row=i, column=1, sticky="w", padx=(10, 0), pady=2)

        # Кнопки действий
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)

# Не уверен что данная кнопка нам нужна, логика не совсем понятно как будем обновлять да и реализацию усложнит
# вполне можно отказатся, но пока есть заглушки (временный код для тестирования пусть будет)
        edit_button = tk.Button(buttons_frame, text="Редактировать профиль",
                                command=lambda: self.on_update_profile(profile_data), width=20, height=1)
        edit_button.pack(side=tk.LEFT, padx=5)

        back_button = tk.Button(buttons_frame, text="Назад в меню", command=self.on_back_to_menu, width=15, height=1)
        back_button.pack(side=tk.LEFT, padx=5)






