import sqlite3
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"
SEED_FILE = BASE_DIR / "data" / "seed_questions.csv"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

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
        FOREIGN KEY (user_id) REFERENCES users(id)
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

    with open(SEED_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
            INSERT INTO questions (category, text, option1, option2, option3, option4, correct_index)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (row["category"], row["text"],
                  row["option1"], row["option2"], row["option3"], row["option4"],
                  int(row["correct_index"])))
    conn.commit()
    conn.close()
    print("[INFO] Database initialized")

if __name__ == "__main__":
    init_db()
