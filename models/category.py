from db import db

class CategoryModel(db.Model):
    
    __tablename__ = "categories"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    posts = db.relationship("PostModel", secondary="post_categories", back_populates="categories")

