from pathlib import Path
from typing import Optional, Dict, Any
from init_db import get_connection
import sqlite3
from datetime import datetime

class UserProfile:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            avatar_path TEXT,
            created_at DATETIME NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            played_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')

        conn.commit()
        conn.close()

    def create_profile(self, name: str, avatar_path: Optional[Path] = None) -> int:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        # Проверка, существует ли пользователь
        cursor.execute('SELECT id FROM users WHERE name = ?', (name,))
        if cursor.fetchone():
            raise ValueError(f"Пользователь с именем '{name}' уже существует")

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        avatar_str = str(avatar_path) if avatar_path else None

        try:
            cursor.execute(
                '''INSERT INTO users (name, avatar_path, created_at)
                VALUES (?, ?, ?)''',
                (name, avatar_str, created_at)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id

        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Ошибка при создании профиля: {e}")
        finally:
            conn.close()

    def load_profile(self, user_id: int) -> Dict[str, Any]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, name, avatar_path, created_at FROM users WHERE id = ?',
            (user_id,)
        )
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        return {
            "id": user_data[0],
            "name": user_data[1],
            "avatar_path": Path(user_data[2]) if user_data[2] else None,
            "created_at": user_data[3]
        }

    def update_profile(self, user_id: int, name: Optional[str] = None, avatar_path: Optional[Path] = None) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if name is not None:
            cursor.execute('SELECT id FROM users WHERE name = ? AND id != ?', (name, user_id))
            if cursor.fetchone():
                conn.close()
                raise ValueError(f"Имя '{name}' уже занято другим пользователем")
            updates.append("name = ?")
            params.append(name)

        if avatar_path is not None:
            updates.append("avatar_path = ?")
            params.append(str(avatar_path))

        if not updates:
            conn.close()
            return

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"

        try:
            cursor.execute(query, params)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Ошибка при обновлении профиля: {e}")
        finally:
            conn.close()

    def save_result(self, user_id: int, score: int, duration_sec: int, category: str) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        played_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute(
                '''INSERT INTO results (user_id, category, score, duration_sec, played_at)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, category, score, duration_sec, played_at)
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Ошибка при сохранении результата: {e}")
        finally:
            conn.close()

    def get_stats(self, user_id: int) -> Dict[str, Any]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        # Общая статистика
        cursor.execute('''
           SELECT 
               COUNT(*) as games_played,
               MAX(score) as best_score,
               AVG(score) as avg_score
           FROM results 
           WHERE user_id = ?
           ''', (user_id,))

        stats = cursor.fetchone()
        if not stats or stats[0] == 0:
            conn.close()
            return {
                "games_played": 0,
                "best_score": 0,
                "avg_score": 0.0,
                "by_category": []
            }

        # Статистика по категориям
        cursor.execute('''
           SELECT 
               category,
               COUNT(*) as games,
               AVG(score) as avg_score
           FROM results 
           WHERE user_id = ?
           GROUP BY category
           ORDER BY games DESC
           ''', (user_id,))

        by_category = []
        for row in cursor.fetchall():
            by_category.append({
                "category": row[0],
                "games": row[1],
                "avg_score": round(float(row[2]), 2)
            })

        conn.close()

        return {
            "games_played": stats[0],
            "best_score": stats[1],
            "avg_score": round(float(stats[2]), 2),
            "by_category": by_category
        }

    def ensure_default_user(self) -> int:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE name = ?', ("Default User",))
        user = cursor.fetchone()

        if user:
            conn.close()
            return user[0]

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute(
                '''INSERT INTO users (name, avatar_path, created_at)
                VALUES (?, ?, ?)''',
                ("Default User", None, created_at)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id

        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Ошибка при создании пользователя по умолчанию: {e}")
        finally:
            conn.close()

    def find_user_id_by_name(self, name: str) -> Optional[int]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE name = ?', (name,))
        user = cursor.fetchone()
        conn.close()

        return user[0] if user else None
