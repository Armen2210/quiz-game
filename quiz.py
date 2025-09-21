from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import sqlite3
import random

START_SECONDS = 20


@dataclass
class Question:
    id: int
    category: str
    text: str
    options: List[str]
    correct_index: int


class QuizGame:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.score = 0
        self.questions = []
        self.current_index = 0

    def list_categories(self) -> List[str]:
        """Получить список доступных категорий из базы данных."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT category FROM questions ORDER BY category")
            categories = [row[0] for row in cur.fetchall()]
        return categories

    def start_game(self, category: str, questions_count: int = 10) -> None:
        """Начать игру с выбором вопросов из указанной категории."""
        self.reset()

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            # Получаем все вопросы из категории
            cur.execute("""
                SELECT id, category, text, option1, option2, option3, option4, correct_index 
                FROM questions 
                WHERE category = ?
            """, (category,))

            rows = cur.fetchall()

        # Если вопросов меньше чем questions_count — брать все
        if len(rows) <= questions_count:
            selected_rows = rows
        else:
            # Случайно выбираем нужное количество вопросов
            selected_rows = random.sample(rows, questions_count)

        # Преобразуем в объекты Question
        for row in selected_rows:
            question = Question(
                id=row[0],
                category=row[1],
                text=row[2],
                options=[row[3], row[4], row[5], row[6]],
                correct_index=row[7]
            )
            self.questions.append(question)

    def get_next_question(self) -> Optional[Question]:
        """Получить следующий вопрос."""
        if self.current_index < len(self.questions):
            question = self.questions[self.current_index]
            self.current_index += 1
            return question
        return None

    def check_answer(self, question_id: int, selected_index: int, time_spent_sec: float) -> bool:
        """Проверить ответ и обновить счет."""
        # Находим вопрос по ID
        current_question = None
        for question in self.questions:
            if question.id == question_id:
                current_question = question
                break

        if current_question is None:
            return False

        # Проверяем правильность ответа
        is_correct = selected_index == current_question.correct_index

        if is_correct:
            # Базовые 100 очков за правильный ответ
            base_points = 100
            # Бонус за скорость: (20 - время) * 5
            speed_bonus = max(0, (START_SECONDS - time_spent_sec) * 5)
            self.score += base_points + int(speed_bonus)

        return is_correct

    def get_score(self) -> int:
        """Получить текущий счет."""
        return self.score

    def get_remaining(self) -> int:
        """Получить количество оставшихся вопросов (включая текущий)."""
        return len(self.questions) - self.current_index

    def reset(self) -> None:
        """Сбросить состояние игры."""
        self.score = 0
        self.questions = []
        self.current_index = 0