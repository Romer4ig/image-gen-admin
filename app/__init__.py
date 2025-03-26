from flask import Flask

def create_app(config_name="development"):
    app = Flask(__name__)
    
    # Загрузка конфигурации
    from app.config.config import config_by_name
    app.config.from_object(config_by_name[config_name])
    
    # Инициализация базы данных
    from app.models import db
    db.init_app(app)

    # Регистрация модулей
    from app.modules import register_modules
    register_modules(app)

    # Регистрация API
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Инициализация менеджера задач
    from app.services.task_manager import init_app as init_task_manager
    init_task_manager(app)
    
    return app
