from app.modules.collections import collections_bp
from app.modules.projects import projects_bp
from app.modules.tasks import tasks_bp
from app.modules.settings import settings_bp

def register_modules(app):
    """Регистрирует все модули в приложении Flask"""
    app.register_blueprint(collections_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(settings_bp)
