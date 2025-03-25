from app.models import db
from datetime import datetime

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('generation_tasks.id'), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('GenerationTask', backref=db.backref('favorites', lazy='dynamic'))
    
    def __repr__(self):
        return f'&lt;Favorite {self.id} for task {self.task_id} - {self.image_path}>'