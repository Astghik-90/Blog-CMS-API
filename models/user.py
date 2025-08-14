from db import db
from enums.roles import UserRole


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(
        db.Integer, default=UserRole.AUTHOR.value, nullable=False
    )
    created_at = db.Column(
        db.DateTime, server_default=db.func.now(), nullable=False
    )

    posts = db.relationship(
        "PostModel", back_populates="author", cascade="all, delete"
    )
