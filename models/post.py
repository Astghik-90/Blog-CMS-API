import uuid
from db import db


class PostModel(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("UserModel", back_populates="posts")

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

    categories = db.relationship(
        "CategoryModel", secondary="post_categories", back_populates="posts"
    )
    comments = db.relationship(
        "CommentModel", back_populates="post", cascade="all, delete"
    )
