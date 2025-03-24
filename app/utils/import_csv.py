import csv
import os
import sys

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.models import db, Collection

def import_collections_from_csv(csv_path):
    """Импорт коллекций из CSV-файла"""
    
    app = create_app('development')
    
    with app.app_context():
        # Удаляем существующие данные
        Collection.query.delete()
        
        # Импортируем данные из CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            
            for row in reader:
                if len(row) >= 4:
                    collection = Collection(
                        id=int(row[0]),
                        title=row[1],
                        type=row[2],
                        prompt=row[3]
                    )
                    db.session.add(collection)
            
            db.session.commit()
            
        print(f"Импортировано {Collection.query.count()} коллекций")

if __name__ == "__main__":
    import_collections_from_csv("Пример базы Для Димы/Лист1-Tаблица 1.csv") 