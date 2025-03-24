from app.models import db
from datetime import datetime

class GenerationTask(db.Model):
    """Модель для хранения задач на генерацию изображений"""
    __tablename__ = 'generation_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
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
    
    # Результат
    result_path = db.Column(db.String(255), nullable=True)
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
    def result_url(self):
        """Возвращает URL для доступа к сгенерированному изображению"""
        if not self.result_path:
            return None
            
        # Преобразуем полный путь в URL для статических файлов
        if 'app/static/' in self.result_path:
            return '/' + '/'.join(self.result_path.split('/', self.result_path.index('static'))[1:])
        return None
    
    def to_dict(self):
        """Преобразует задачу в словарь для API"""
        return {
            'id': self.id,
            'prompt': self.prompt,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'collection_id': self.collection_id,
            'project_id': self.project_id,
            'result_url': self.result_url
        } 