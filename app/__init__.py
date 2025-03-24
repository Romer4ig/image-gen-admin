from flask import Flask

def create_app(config_name="development"):
    app = Flask(__name__)
    
    # Загрузка конфигурации
    from app.config.config import config_by_name
    app.config.from_object(config_by_name[config_name])
    
    # Инициализация базы данных
    from app.models import db
    db.init_app(app)
    
    # Регистрация blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Регистрация web blueprint
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    # Инициализация менеджера задач
    from app.services.task_manager import task_manager
    task_manager.init_app(app)
    
    # Вместо before_first_request используем запуск воркера через функцию на первом запросе
    @app.after_request
    def start_worker_after_first_request(response):
        # Статический флаг, чтобы запустить только один раз
        if not hasattr(app, '_worker_started'):
            with app.app_context():
                task_manager.ensure_worker_running()
            app._worker_started = True
        return response
    
    return app
