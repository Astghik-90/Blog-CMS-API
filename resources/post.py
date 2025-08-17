import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from db import db
from models import PostModel, CategoryModel
from schemas import PlainPostSchema, PostResponseSchema, PostCreationSchema, PostUpdateSchema

from sqlalchemy.exc import SQLAlchemyError, IntegrityError     

blp = Blueprint("Post", __name__, description="Operations on stores")

@blp.route("/post")
class PostList(MethodView):
    @jwt_required()
    @blp.response(200, PlainPostSchema(many=True))
    def get(self):
        return PostModel.query.all()
    
    @jwt_required()
    @blp.arguments(PostCreationSchema)
    @blp.response(201, PostResponseSchema)
    def post(self, post_data):
        category_names = post_data.pop("category_names", [])
        post = PostModel(**post_data)

        if category_names:
            categories = CategoryModel.query.filter(CategoryModel.name.in_(category_names)).all()

            if len(categories) != len(category_names):
                abort(404, message="One or more categories not found.")
            
            post.categories = categories
        
        post.author_id = get_jwt_identity()
        
        try:
            db.session.add(post)
            db.session.commit()   
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the post.")
        
        return post, 201

@blp.route("/post/<uuid:post_id>")
class Post(MethodView):
    @jwt_required()
    @blp.response(200, PostResponseSchema)
    def get(self, post_id):
        post = PostModel.query.get_or_404(str(post_id))
        return post, 200

    @jwt_required()
    @blp.arguments(PostUpdateSchema)
    @blp.response(200, PostResponseSchema)
    def put(self, post_data, post_id):
        post = PostModel.query.get_or_404(str(post_id))
        
        # Check authorization - only author or admin can update
        jwt_identity = get_jwt_identity()
        jwt = get_jwt()
        
        if post.author_id != jwt_identity and jwt["role"] != 1:  # 1 = ADMIN
            abort(403, message="Access forbidden. Only the author or admin can update this post.")
        
        for key, value in post_data.items():
            setattr(post, key, value)
        
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the post.")
        
        return post, 200
    
    @jwt_required()
    @blp.response(204)
    def delete(self, post_id):
        post = PostModel.query.get_or_404(str(post_id))
        
        # Check authorization - only author or admin can delete
        jwt_identity = get_jwt_identity()
        jwt = get_jwt()
        
        if post.author_id != jwt_identity and jwt["role"] != 1:  # 1 = ADMIN
            abort(403, message="Access forbidden. Only the author or admin can delete this post.")
        
        try:
            db.session.delete(post)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the post.")
        
        return {"message": "Post deleted successfully"}, 204

