import sqlite3
import csv
from pathlib import Path

def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database(db_path: Path) -> None:

    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avatar_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            played_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            text TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_index INTEGER NOT NULL CHECK (correct_index BETWEEN 0 AND 3)
        )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_user ON results(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_category ON results(category)')

        cursor.execute('SELECT COUNT(*) FROM questions')
        count = cursor.fetchone()[0]

        if count == 0:
            seed_path = Path('data') / 'seed_questions.csv'

            if not seed_path.exists():
                print(f" Файл {seed_path} не найден. Пропускаем загрузку вопросов.")
                conn.commit()
                return

            with open(seed_path, 'r', encoding='utf-8', newline='') as file:
                csv_reader = csv.DictReader(file)

                for row in csv_reader:

                    if (not row['category'] or not row['text'] or
                            not row['option1'] or not row['option2'] or
                            not row['option3'] or not row['option4']):
                        print(f" Пропуск строки с пустыми полями: {row}")
                        continue

                    try:
                        correct_index = int(row['correct_index'])
                        if correct_index not in {0, 1, 2, 3}:
                            print(f" Некорректный correct_index: {correct_index} в строке: {row}")
                            continue
                    except ValueError:
                        print(f" Некорректный correct_index: {row['correct_index']} в строке: {row}")
                        continue


                    cursor.execute('''
                    INSERT INTO questions (category, text, option1, option2, option3, option4, correct_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['category'],
                        row['text'],
                        row['option1'],
                        row['option2'],
                        row['option3'],
                        row['option4'],
                        correct_index
                    ))

            print(f"Загружено {cursor.rowcount} вопросов из {seed_path}")

        conn.commit()
        print(f" База данных инициализирована: {db_path}")

    except Exception as e:
        conn.rollback()
        raise Exception(f" Ошибка при инициализации БД: {e}")
    finally:
        conn.close()