from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Импорт моделей
# from app.models.user import User
from app.models.collection import Collection
from app.models.project import Project
from app.models.generation_task import GenerationTask
