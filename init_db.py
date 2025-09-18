import sqlite3
import csv
import os
from pathlib import Path


def get_connection(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_question_database():
    conn = sqlite3.connect('quiz_questions.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        category TEXT NOT NULL,
        text TEXT NOT NULL,
        option1 TEXT NOT NULL,
        option2 TEXT NOT NULL,
        option3 TEXT NOT NULL,
        option4 TEXT NOT NULL,
        correct_index INTEGER NOT NULL
    )
    ''')

    csv_file_path = 'questions.csv'
    if not os.path.exists(csv_file_path):
        print(f"Ошибка: Файл '{csv_file_path}' не найден! Убедитесь, что он в папке проекта.")
        return

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            cursor.execute('''
            INSERT OR REPLACE INTO questions (id, category, text, option1, option2, option3, option4, correct_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(row['id']),
                row['category'],
                row['text'],
                row['option1'],
                row['option2'],
                row['option3'],
                row['option4'],
                int(row['correct_index'])
            ))
    conn.commit()
    conn.close()
    print("✅ Вопросы успешно импортированы из CSV в базу данных!")
