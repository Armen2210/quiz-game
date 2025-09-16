from pathlib import Path
from typing import Optional, Dict, Any

class UserProfile:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def create_profile(self, name: str, avatar_path: Optional[Path] = None) -> int:
        print(f"[User] Create profile: {name}")
        return 1

    def load_profile(self, user_id: int) -> Dict[str, Any]:
        return {"id": user_id, "name": "Player1", "avatar": None}

    def update_profile(self, user_id: int, name: Optional[str] = None, avatar_path: Optional[Path] = None) -> None:
        print(f"[User] Update profile {user_id}")

    def save_result(self, user_id: int, score: int, duration_sec: int, category: str) -> None:
        print(f"[User] Save result: {score}")

    def get_stats(self, user_id: int) -> Dict[str, Any]:
        return {"games_played": 0, "best_score": 0, "avg_score": 0}

    def ensure_default_user(self) -> int:
        return 1
