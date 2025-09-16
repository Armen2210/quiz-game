# quiz-game
интерактивная викторина, в которой пользователи смогут отвечать на вопросы из разных категорий и накапливать очки


🎮 Quiz Game

Интерактивная игра-викторина на Python.
Проект делается командой из 4 человек: интерфейс, игровая логика, профиль/статистика, интеграция.

🚀 Установка и запуск
1. Клонировать проект
git clone <URL_репозитория>
cd quiz-game

2. Создать виртуальное окружение

(рекомендуется для изоляции пакетов)

python -m venv .venv


Активация:

Windows

.venv\Scripts\activate


Linux / Mac

source .venv/bin/activate

3. Установить зависимости
pip install -r requirements.txt

4. Инициализировать базу данных
python scripts/init_db.py

5. Запустить игру
python main.py

🛠️ Используемые технологии

Python 3.11+

Tkinter (интерфейс)

SQLite (база данных)

Pillow (аватары, опционально)

Pytest (тесты)

👥 Работа с GitHub (через GitHub Desktop или терминал)

У каждого своя ветка:

Антон → feature/ui-anton

Сергей → feature/quiz-sergey

Катрин → feature/user-katrin

Армен → feature/integration-armen

Последовательность работы:

Сделал изменения → Commit → Push в свою ветку.

Создал Pull Request в main.

Тимлид проверяет и делает Merge.

После Merge:

Обновить main.

В своей ветке нажать Update from main (в GitHub Desktop).

📂 Структура проекта
quiz-game/
│
├─ data/
│   ├─ seed_questions.csv   # вопросы для викторины
│   └─ avatars/             # картинки-аватары
├─ scripts/
│   └─ init_db.py           # инициализация базы данных
├─ main.py                  # точка входа (интеграция)
├─ ui.py                    # интерфейс (Антон)
├─ quiz.py                  # логика викторины (Сергей)
├─ user.py                  # профиль и статистика (Катрин)
├─ requirements.txt         # зависимости
├─ README.md                # эта инструкция
└─ .gitignore

📌 Примечания

Все пути к файлам должны быть относительными (Path), без абсолютных.

База app.db не хранится в Git, она создаётся автоматически.

Перед сдачей работы проверяйте, что python main.py запускает игру без ошибок.