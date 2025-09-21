from pathlib import Path
from typing import Optional, Dict, Any
from init_db import get_connection, init_database
import sqlite3
from datetime import datetime

class UserProfile:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        init_database(db_path)

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
        except Exception as e:
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
            "avatar": user_data[2],
            "created_at": user_data[3]
        }

    def update_profile(self, user_id: int, name: Optional[str] = None, avatar_path: Optional[Path] = None) -> None:

        updates = []
        params = []

        if name is not None:
            if not name.strip():
                raise ValueError("Имя пользователя не может быть пустым")
            updates.append("name = ?")
            params.append(name.strip())

        if avatar_path is not None:
            updates.append("avatar_path = ?")
            params.append(str(avatar_path))

        if not updates:
            return

        params.append(user_id)

        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        try:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"Имя '{name}' уже занято другим пользователем")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка при обновлении профиля: {e}")
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

        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка при сохранении результата: {e}")
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

        by_category = []
        for row in cursor.fetchall():
            by_category.append({
                "category": row[0],
                "games": row[1],
                "avg_score": round(float(row[2]), 2)
            })

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
            cursor.execute(
                'SELECT id FROM users WHERE name = ?',
                ('Player1',)
            )
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

        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка при создании пользователя по умолчанию: {e}")
        finally:
            conn.close()
