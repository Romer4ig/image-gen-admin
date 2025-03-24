import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Базовая конфигурация"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-12345')
    DEBUG = False


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "dev.db")}')


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
