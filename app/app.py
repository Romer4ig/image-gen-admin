from app import create_app
from app.models import db, Collection
import os
import sqlite3

app = create_app(os.getenv('FLASK_ENV', 'development'))

# SQLAlchemy уже инициализирована в create_app(), поэтому здесь не нужно это делать

with app.app_context():
    # Создать таблицы через SQLAlchemy
    db.create_all()
    
    # Проверить наличие данных в таблице collections
    count = Collection.query.count()
    
    # Если таблица пуста, импортировать данные из SQLite напрямую
    if count == 0:
        # Получаем путь к базе данных
        base_dir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(os.path.dirname(base_dir), 'dev.db')
        
        if os.path.exists(db_path):
            # Подключаемся к файлу SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Проверяем наличие таблицы collections
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collections'")
            if cursor.fetchone():
                # Получаем данные из таблицы
                cursor.execute("SELECT id, title, type, prompt FROM collections")
                rows = cursor.fetchall()
                
                # Добавляем данные в SQLAlchemy модели
                for row in rows:
                    collection = Collection(
                        id=row[0],
                        title=row[1],
                        type=row[2],
                        prompt=row[3]
                    )
                    db.session.add(collection)
                
                # Сохраняем изменения
                db.session.commit()
                print(f"Импортировано {len(rows)} коллекций из SQLite в SQLAlchemy")
            
            conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
