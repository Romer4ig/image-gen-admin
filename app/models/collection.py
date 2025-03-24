from app.models import db

class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    prompt = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Collection {self.id}: {self.title}>' 