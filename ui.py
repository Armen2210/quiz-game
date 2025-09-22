import tkinter as tk
from tkinter import simpledialog, filedialog
from quiz import Question
from typing import List, Optional, Dict, Any, Callable
from PIL import Image, ImageTk

class QuizUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Game")
        self.geometry("600x700")
        self.timer_id = None
        self.total_seconds = 0
        self._categories: List[str] = []
        self.current_question_id = None

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
        self.on_answer(self.current_question_id, idx, spent)

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
            self.on_time_up(self.current_question_id, self.total_seconds)

    def _edit_profile(self, profile_data: dict):
        """Диалог редактирования профиля"""
        try:
            # Запрос имени
            new_name = simpledialog.askstring(
                "Редактирование профиля",
                "Введите новое имя:",
                initialvalue=profile_data.get("name", "")
            )
            # Если пользователь нажал Cancel
            if new_name is None:
                return
            
            # Безопасный запрос аватара
            avatar_path = None
            try:
                # Спрашиваем, хочет ли пользователь выбрать аватар
                import tkinter.messagebox as messagebox
                want_avatar = messagebox.askyesno(
                    "Аватар", 
                    "Хотите выбрать аватар?"
                )
                
                if want_avatar:
                    # Безопасный вызов filedialog с дополнительными проверками
                    try:
                        avatar_path = filedialog.askopenfilename(
                            title="Выберите аватар",
                            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")]
                        )
                        # Если пользователь отменил выбор, avatar_path будет пустой строкой
                        if not avatar_path:
                            avatar_path = None
                    except Exception as dialog_error:
                        print(f"[WARNING] Avatar selection failed: {dialog_error}")
                        avatar_path = None
                        messagebox.showinfo("Информация", "Выбор аватара недоступен, сохраняем только имя")
                        
            except Exception as avatar_error:
                print(f"[WARNING] Avatar dialog error: {avatar_error}")
                avatar_path = None
            
            # Обновляем профиль (имя и аватар если выбран)
            self.on_update_profile(new_name, avatar_path)
            
        except Exception as e:
            print(f"[ERROR] Error in _edit_profile: {e}")
            # Возвращаемся к профилю в случае ошибки
            if hasattr(self, 'on_back_to_menu'):
                self.on_back_to_menu()


    def bind_actions(self,
                     on_start_game: Callable[[str], None],
                     on_answer: Callable[[int, int, int], None],
                     on_time_up: Callable[[int, int], None],
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


    def show_category_menu(self, categories: List[str]):
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
                "sport": "Спорт",
                "geography": "География"
            }

            display_name = category_names.get(category, category.capitalize())

            # Создаем кнопку категории
            category_btn = tk.Button(categories_frame,
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
        self.current_question_id = question.id

        # Сохраняем время
        self.total_seconds = int(timer_sec)
        self.current_time = int(timer_sec)

        # Основной фрейм
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Верхняя панель
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

        # Текст вопроса
        question_frame = tk.Frame(main_frame)
        question_frame.pack(fill=tk.X, pady=20)
        question_label = tk.Label(question_frame, text=question.text,
                                  font=("Arial", 14), wraplength=450, justify=tk.CENTER)
        question_label.pack()

        # Фрейм для вариантов ответов
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        # СОЗДАЕМ КНОПКИ - ИСПРАВЛЕННЫЙ КОД
        self.option_buttons = []
        for i, opt in enumerate(question.options):  # ← opt, не option!
            btn = tk.Button(options_frame,
                            text=opt,  # ← исправлено на opt
                            command=lambda idx=i: self._on_answer_click(idx),  # ← исправлено на _on_answer_click
                            width=40,
                            height=2,
                            font=("Arial", 11),
                            bg="#e8f4f8",
                            relief=tk.RAISED,
                            wraplength=400)
            btn.pack(pady=8)
            self.option_buttons.append(btn)

        # Кнопка выхода
        exit_button = tk.Button(main_frame,
                                text="Выход в меню",
                                command=self.on_back_to_menu,
                                width=15,
                                height=1,
                                font=("Arial", 10),
                                bg="#ffcccc")
        exit_button.pack(pady=10)

        # Запускаем таймер
        self.timer_id = self.after(1000, self._tick)


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
        buttons_frame.pack(pady=10)

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
        """Показывает экран профиля с статистикой"""
        self._cancel_timer_if_any()

        # Очищаем окно
        for widget in self.winfo_children():
            widget.destroy()

        # Мягкий маппинг статистики (совместимость со старым и новым форматом)
        games_played = stats.get("games_played", stats.get("total_games", 0))
        best_score = stats.get("best_score", 0)
        avg_score = stats.get("avg_score", stats.get("average_score", 0.0))
        by_category = stats.get("by_category", [])

        # Защита: преобразуем dict в list если нужно
        if isinstance(by_category, dict):
            by_category = [
                {
                    "category": k,
                    "games": v.get("games", 0) if isinstance(v, dict) else 0,
                    "avg_score": v.get("avg_score", 0.0) if isinstance(v, dict) else 0.0
                }
                for k, v in by_category.items()
            ]

        # Основной фрейм с прокруткой
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

        # --- аватар (если есть) ---
        avatar_path = profile_data.get("avatar")
        if avatar_path:
            print(f"[DEBUG] Trying to load avatar: {avatar_path}")
            try:
                import os
                if not os.path.exists(avatar_path):
                    print(f"[WARNING] Avatar file not found: {avatar_path}")
                else:
                    print(f"[DEBUG] Avatar file exists, loading...")
                    img = Image.open(avatar_path)
                    print(f"[DEBUG] Original image size: {img.size}, mode: {img.mode}")
                    
                    # Конвертируем в RGB если нужно
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                        print(f"[DEBUG] Converted to RGB mode")
                    
                    img = img.resize((120, 120), Image.LANCZOS)
                    print(f"[DEBUG] Resized to: {img.size}")
                    
                    photo = ImageTk.PhotoImage(img)
                    print(f"[DEBUG] Created PhotoImage successfully")

                    # сохраняем в self, а не в локальную переменную
                    self.avatar_photo = photo

                    avatar_label = tk.Label(user_frame, image=self.avatar_photo, bd=2, relief="solid")
                    avatar_label.grid(row=1, column=0, columnspan=2, pady=10)
                    print(f"[DEBUG] Avatar displayed successfully")
            except Exception as e:
                print(f"[ERROR] Ошибка загрузки аватара: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[DEBUG] No avatar path in profile data")

        # Общая статистика
        stats_frame = tk.LabelFrame(main_frame, text="Общая статистика", font=("Arial", 14, "bold"))
        stats_frame.pack(fill=tk.X, pady=20)

        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(padx=10, pady=10)

        stat_rows = [
            ("Всего игр", games_played),
            ("Лучший счет", best_score),
            ("Средний счет", f"{avg_score:.2f}")
        ]

        for i, (label, value) in enumerate(stat_rows):
            tk.Label(stats_grid, text=label + ":", font=("Arial", 11, "bold")).grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(stats_grid, text=str(value), font=("Arial", 11)).grid(row=i, column=1, sticky="w", padx=(10, 0),
                                                                           pady=2)

        # Статистика по категориям
        if by_category:
            cat_frame = tk.LabelFrame(main_frame, text="Статистика по категориям", font=("Arial", 14, "bold"))
            cat_frame.pack(fill=tk.X, pady=20)

            cat_grid = tk.Frame(cat_frame)
            cat_grid.pack(padx=10, pady=10)

            # Заголовки таблицы
            tk.Label(cat_grid, text="Категория", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, pady=2)
            tk.Label(cat_grid, text="Игр", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=5, pady=2)
            tk.Label(cat_grid, text="Средний счет", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=5, pady=2)

            # Данные по категориям
            for i, cat_stat in enumerate(by_category, 1):
                category_name = cat_stat.get("category", "Неизвестно")
                games = cat_stat.get("games", 0)
                avg_score = cat_stat.get("avg_score", 0.0)

                # Определяем русское название категории
                category_names = {
                    "history": "История",
                    "science": "Наука",
                    "culture": "Культура",
                    "sport": "Спорт",
                    "geography": "География"
                }

                display_name = category_names.get(category_name, category_name.capitalize())

                tk.Label(cat_grid, text=display_name, font=("Arial", 11)).grid(row=i, column=0, sticky="w", padx=5,
                                                                               pady=2)
                tk.Label(cat_grid, text=str(games), font=("Arial", 11)).grid(row=i, column=1, padx=5, pady=2)
                tk.Label(cat_grid, text=f"{avg_score:.2f}", font=("Arial", 11)).grid(row=i, column=2, padx=5, pady=2)

        # Кнопки действий
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        print("[DEBUG] Created buttons_frame")

        edit_button = tk.Button(buttons_frame, text="Редактировать профиль",
                                command=lambda: self._edit_profile(profile_data),
                                width=20, height=1,
                                bg="lightgray", fg="black",
                                font=("Arial", 10, "bold"))
        edit_button.pack(side=tk.LEFT, padx=5)
        print("[DEBUG] Created edit_button")

        back_button = tk.Button(buttons_frame, text="Назад в меню",
                                command=self.on_back_to_menu,
                                width=15, height=1,
                                bg="lightblue", fg="black",
                                font=("Arial", 10, "bold"))
        back_button.pack(side=tk.LEFT, padx=5)
        print("[DEBUG] Created back_button")
        
        # Проверяем, что метод привязан
        if hasattr(self, 'on_back_to_menu'):
            print("[DEBUG] on_back_to_menu method is bound")
        else:
            print("[ERROR] on_back_to_menu method is NOT bound!")