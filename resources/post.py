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
            
            if len(categories != category_names):
                abort(404, message="One or more categories not found.")
            
            post.categories = categories
        
        try:
            db.session.add(post)
            db.session.commit()   
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the post.")
        
        return post, 201
    
    @jwt_required()   
    @blp.route("/post/<int:post_id>")
    class Post(MethodView):
        @blp.response(200, PostResponseSchema)
        def get(self, post_id):
            post = PostModel.query.get_or_404(post_id)
            return post, 200

        @blp.arguments(PostUpdateSchema)
        @blp.response(200, PostResponseSchema)
        def put(self, post_data, post_id):
            post = PostModel.query.get_or_404(post_id)
            
            for key, value in post_data.items():
                setattr(post, key, value)
            
            return post, 200
        
        @jwt_required()
        @blp.response(204)
        def delete(self, post_id):
            post = PostModel.query.get_or_404(post_id)
            
            try:
                db.session.delete(post)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="An error occurred while deleting the post.")
            
            return {"message": "Post deleted successfully"}, 204
            
            