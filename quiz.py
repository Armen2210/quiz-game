from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

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

    def start_game(self, category: str, questions_count: int = 10) -> None:
        print(f"[Quiz] Start game with category: {category}")
        # TODO: Выборка из базы

    def get_next_question(self) -> Optional[Question]:
        print("[Quiz] Get next question")
        return None

    def check_answer(self, question_id: int, selected_index: int, time_spent_sec: float) -> bool:
        print("[Quiz] Check answer")
        return False

    def get_score(self) -> int:
        return self.score

    def get_remaining(self) -> int:
        return len(self.questions) - self.current_index

    def reset(self) -> None:
        self.score = 0
        self.questions = []
        self.current_index = 0
