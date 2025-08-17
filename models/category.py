import uuid
from db import db

class CategoryModel(db.Model):
    
    __tablename__ = "categories"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    posts = db.relationship("PostModel", secondary="post_categories", back_populates="categories")

