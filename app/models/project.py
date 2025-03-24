from app.models import db

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    basic_prompt = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Project {self.id}: {self.title}>' 