# Flask API Приложение

## Установка

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Linux/Mac
source venv/bin/activate
# Windows
# venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

## Запуск

```bash
# Разработка
flask run

# Или
python app/app.py
```

## Структура проекта

```
app/
|-- api/              # API маршруты и контроллеры
|-- models/           # Модели данных
|-- services/         # Бизнес-логика
|-- config/           # Конфигурации
|-- utils/            # Утилиты и вспомогательные функции
|-- templates/        # Шаблоны (если нужны)
|-- static/           # Статические файлы
|-- app.py            # Точка входа
|-- __init__.py       # Фабрика приложения
```
