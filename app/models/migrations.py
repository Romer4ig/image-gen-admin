"""
Скрипт миграции базы данных для добавления поддержки пакетной генерации
"""

from app.models import db
import sqlite3
import os
from flask import current_app

def run_migrations():
    """Запускает необходимые миграции для базы данных"""
    print("Запуск миграций...")
    
    # Получаем путь к базе данных
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        # Если путь относительный, добавим базовый путь
        if not os.path.isabs(db_path):
            db_path = os.path.join(current_app.instance_path, db_path)
    else:
        print("Используется не SQLite база данных. Миграция не требуется.")
        return
    
    # Проверяем существование файла базы данных
    if not os.path.exists(db_path):
        print(f"База данных не найдена по пути: {db_path}")
        return
    
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем, существуют ли уже новые колонки
    cursor.execute("PRAGMA table_info(generation_tasks)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    # Добавляем колонки для пакетной генерации, если их еще нет
    if 'is_batch' not in column_names:
        print("Добавление колонки is_batch...")
        cursor.execute("ALTER TABLE generation_tasks ADD COLUMN is_batch BOOLEAN DEFAULT 0")
    
    if 'batch_size' not in column_names:
        print("Добавление колонки batch_size...")
        cursor.execute("ALTER TABLE generation_tasks ADD COLUMN batch_size INTEGER DEFAULT 1")
    
    if 'batch_count' not in column_names:
        print("Добавление колонки batch_count...")
        cursor.execute("ALTER TABLE generation_tasks ADD COLUMN batch_count INTEGER")
    
    if 'result_paths' not in column_names:
        print("Добавление колонки result_paths...")
        cursor.execute("ALTER TABLE generation_tasks ADD COLUMN result_paths TEXT")
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    print("Миграции успешно выполнены.")

if __name__ == "__main__":
    # Этот код будет выполнен при запуске скрипта напрямую
    from app import create_app
    app = create_app()
    with app.app_context():
        run_migrations() 