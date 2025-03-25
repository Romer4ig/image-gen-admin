from app.models import db
import json

class Settings(db.Model):
    """Модель для хранения настроек приложения"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    
    @staticmethod
    def get_setting(key):
        """Получение значения настройки по ключу"""
        setting = Settings.query.filter_by(key=key).first()
        if not setting:
            return None
        try:
            return json.loads(setting.value)
        except:
            return setting.value
    
    @staticmethod
    def set_setting(key, value):
        """Установка значения настройки"""
        setting = Settings.query.filter_by(key=key).first()
        if not setting:
            setting = Settings(key=key)
        
        # Если значение не строковое, конвертируем в JSON
        if not isinstance(value, str):
            value = json.dumps(value)
        
        setting.value = value
        db.session.add(setting)
        db.session.commit()
        return setting
        
    @staticmethod
    def get_all_settings():
        """Получение всех настроек в виде словаря"""
        settings = Settings.query.all()
        result = {}
        for setting in settings:
            try:
                result[setting.key] = json.loads(setting.value)
            except:
                result[setting.key] = setting.value
        return result
    
    def __repr__(self):
        return f"<Setting {self.key}>" 