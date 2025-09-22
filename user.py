from pathlib import Path
from typing import Optional, Dict, Any
from scripts.init_db import get_connection
import sqlite3
from datetime import datetime


class UserProfile:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def create_profile(self, name: str, avatar_path: Optional[Path] = None) -> int:
        if not name.strip():
            raise ValueError("Имя пользователя не может быть пустым")

        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        try:
            avatar_str = str(avatar_path) if avatar_path else None
            created_at = datetime.now().isoformat()

            cursor.execute(
                'INSERT INTO users (name, avatar_path, created_at) VALUES (?, ?, ?)',
                (name.strip(), avatar_str, created_at)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id

        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"Пользователь с именем '{name}' уже существует")
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
            "avatar": user_data[2],
            "created_at": user_data[3]
        }

    def update_profile(self, user_id: int, name: Optional[str] = None, avatar_path: Optional[Path] = None) -> None:
        updates = []
        params = []

        # Загружаем текущие данные пользователя
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            raise ValueError(f"Пользователь с ID {user_id} не найден")
        current_name = result[0]

        # Обновляем имя только если оно реально изменилось
        if name is not None and name.strip() and name.strip() != current_name:
            updates.append("name = ?")
            params.append(name.strip())

        if avatar_path is not None:
            updates.append("avatar_path = ?")
            params.append(str(avatar_path))

        if not updates:  # нечего обновлять
            conn.close()
            return

        params.append(user_id)

        try:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            # Проверяем, не пытается ли пользователь установить своё же имя
            if name and name.strip() == current_name:
                # Это нормально - пользователь не меняет имя
                pass
            else:
                # Проверяем, занято ли имя другим пользователем
                cursor.execute("SELECT id FROM users WHERE name = ? AND id != ?", (name.strip(), user_id))
                existing_user = cursor.fetchone()
                if existing_user:
                    raise ValueError(f"Имя '{name}' уже занято другим пользователем")
                else:
                    # Другая ошибка целостности
                    raise ValueError("Ошибка при обновлении профиля")
        finally:
            conn.close()

    def save_result(self, user_id: int, score: int, duration_sec: int, category: str) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        try:
            played_at = datetime.now().isoformat()
            cursor.execute(
                '''INSERT INTO results (user_id, category, score, duration_sec, played_at)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, category, score, duration_sec, played_at)
            )
            conn.commit()
        finally:
            conn.close()

    def get_stats(self, user_id: int) -> Dict[str, Any]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                COUNT(*) as games_played,
                COALESCE(MAX(score), 0) as best_score,
                COALESCE(AVG(score), 0.0) as avg_score
            FROM results 
            WHERE user_id = ?
        ''', (user_id,))
        stats = cursor.fetchone()

        cursor.execute('''
            SELECT 
                category,
                COUNT(*) as games,
                COALESCE(AVG(score), 0.0) as avg_score
            FROM results 
            WHERE user_id = ?
            GROUP BY category
            ORDER BY category
        ''', (user_id,))
        by_category = [
            {"category": row[0], "games": row[1], "avg_score": round(float(row[2]), 2)}
            for row in cursor.fetchall()
        ]
        conn.close()

        return {
            "games_played": stats[0] if stats else 0,
            "best_score": stats[1] if stats else 0,
            "avg_score": round(float(stats[2]), 2) if stats and stats[2] is not None else 0.0,
            "by_category": by_category
        }

    def ensure_default_user(self) -> int:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT id FROM users WHERE name = ?', ('Player1',))
            user = cursor.fetchone()
            if user:
                return user[0]

            created_at = datetime.now().isoformat()
            cursor.execute(
                'INSERT INTO users (name, created_at) VALUES (?, ?)',
                ('Player1', created_at)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        finally:
            conn.close()
