import os
from app.models import db
from datetime import datetime

class GenerationTask(db.Model):
    """Модель для хранения задач на генерацию изображений"""
    __tablename__ = 'generation_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    negative_prompt = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Параметры генерации
    width = db.Column(db.Integer, default=640)
    height = db.Column(db.Integer, default=640)
    steps = db.Column(db.Integer, default=22)
    sampler_name = db.Column(db.String(50), default='Euler a')
    cfg_scale = db.Column(db.Float, default=7.0)
    
    # Параметры изображений
    batch_size = db.Column(db.Integer, default=1)  # Планируемое количество изображений
    batch_count = db.Column(db.Integer, nullable=True)  # Фактическое количество сгенерированных изображений
    result_paths = db.Column(db.Text, nullable=True)  # Пути ко всем изображениям, разделенные точкой с запятой
        
    error = db.Column(db.Text, nullable=True)
    
    # Связи с другими моделями
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    
    # Связи
    collection = db.relationship('Collection', backref=db.backref('generation_tasks', lazy='dynamic'))
    project = db.relationship('Project', backref=db.backref('generation_tasks', lazy='dynamic'))
    
    def __repr__(self):
        return f'<GenerationTask {self.id}: {self.status}>'

    @property
    def result_urls(self):
        """
        Преобразует пути к файлам в URL для веб-доступа
        
        Returns:
            list: Список URL для доступа к изображениям
        """
        if not self.result_paths:
            return []
                
        urls = []
        for path in self.result_paths.split(';'):
            urls.append(path.replace('app',''))
            
        return urls
    
    def to_dict(self):
        """Преобразует задачу в словарь для API"""
        result = {
            'id': self.id,
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'collection_id': self.collection_id,
            'project_id': self.project_id,
            'result_url': self.result_url,
            'batch_size': self.batch_size
        }
        
        # Добавляем информацию о пакетной генерации, если это пакетная задача
        if self.batch_count:
            result['batch_count'] = self.batch_count
            result['result_urls'] = self.result_urls
        
        return result 