import uuid
from db import db


class CommentModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)

    post_id = db.Column(db.String(36), db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    post = db.relationship("PostModel", back_populates="comments")
    user = db.relationship("UserModel", back_populates="comments")
