import sqlite3
from pathlib import Path
import csv


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(db_path)
    cur = conn.cursor()

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avatar_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            played_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            text TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_index INTEGER NOT NULL CHECK (correct_index BETWEEN 0 AND 3)
        )""")

        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_name ON users(name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_results_user ON results(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_results_category ON results(category)")

        cur.execute("SELECT COUNT(*) FROM questions")
        count = cur.fetchone()[0]

        if count > 0:
            print("[INFO] Questions table not empty, seeding skipped.")
            conn.commit()
            return

        seed_file = db_path.parent / "seed_questions.csv"

        if not seed_file.exists():
            print(f"[WARNING] The file {seed_file} was not found. Question loading will be skipped.")
            conn.commit()
            return

        inserted = 0

        with open(seed_file, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            # Проверка заголовка CSV
            expected_header = ["category", "text", "option1", "option2", "option3", "option4", "correct_index"]
            if reader.fieldnames != expected_header:
                raise ValueError(f"Invalid CSV header. Expected: {expected_header}, Got: {reader.fieldnames}")

            for row in reader:
                # Проверка на пустые значения
                if (not row.get('category') or not row.get('text') or
                        not row.get('option1') or not row.get('option2') or
                        not row.get('option3') or not row.get('option4') or
                        not row.get('correct_index')):
                    print(f"[WARNING] Empty values in row skipped: {row}")
                    continue

                # Валидация correct_index
                try:
                    ci = int(row["correct_index"])
                    if ci not in {0, 1, 2, 3}:
                        print(f"[SKIP] invalid correct_index: {ci}, row={row}")
                        continue
                except ValueError:
                    print(f"[SKIP] non-integer correct_index: {row['correct_index']}, row={row}")
                    continue

                # Вставка вопроса
                cur.execute("""
                        INSERT INTO questions (category, text, option1, option2, option3, option4, correct_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (row["category"], row["text"],
                              row["option1"], row["option2"], row["option3"], row["option4"],
                              ci))
                inserted += 1

        print(f"[INFO] Seeded {inserted} questions from {seed_file}")
        conn.commit()
        print("[INFO] Database initialized")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Database initialization error: {e}")
        raise
    finally:
        conn.close()

