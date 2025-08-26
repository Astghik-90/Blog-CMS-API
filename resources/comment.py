from flask import request
from flask.views import MethodView
from enums.roles import UserRole
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import CommentModel, PostModel, UserModel
from schemas import CommentSchema, PlainCommentSchema

blp = Blueprint("Comment", __name__, description="Operations on comments")

@blp.route("/comments")
class AllCommentsList(MethodView):
    # get all comments (admin only)
    @jwt_required()
    @blp.response(200, CommentSchema(many=True))
    def get(self):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN.value:
            abort(403, message="Access forbidden. Admin access required.")
        
        comments = CommentModel.query.all()
        return comments

@blp.route("/posts/<uuid:post_id>/comments")
class PostCommentList(MethodView):
    # get all comments of the post
    @jwt_required()
    @blp.response(200, PlainCommentSchema(many=True))
    def get(self, post_id):
        post = PostModel.query.get_or_404(str(post_id))
        return post.comments

    # create comment for the post
    @jwt_required()
    @blp.arguments(PlainCommentSchema)
    @blp.response(201, CommentSchema)
    def post(self, comment_data, post_id):
        # Verify post exists
        post = PostModel.query.get_or_404(str(post_id))
        
        comment = CommentModel(**comment_data)
        comment.post_id = str(post_id)
        comment.user_id = get_jwt_identity()
        
        try:
            db.session.add(comment)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the comment.")
        return comment

@blp.route("/comments/<uuid:comment_id>")
class Comment(MethodView):
    # get comment details by ID
    @jwt_required()
    @blp.response(200, CommentSchema)
    def get(self, comment_id):
        comment = CommentModel.query.get_or_404(str(comment_id))
        return comment, 200

    # delete comment
    @jwt_required(fresh=True)
    @blp.response(204)
    def delete(self, comment_id):
        comment = CommentModel.query.get_or_404(str(comment_id))
        jwt_identity = get_jwt_identity()
        jwt = get_jwt()
        #  Admin, comment owner, or post author
        if (jwt["role"] != UserRole.ADMIN.value and 
            jwt_identity != comment.user_id and 
            jwt_identity != comment.post.author_id):
            abort(403, message="Access forbidden.")
        try:
            db.session.delete(comment)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the comment.")
        return ""
    
    @jwt_required()  
    @blp.arguments(PlainCommentSchema)
    @blp.response(200, CommentSchema)
    def put(self, comment_id, comment_data):
        comment = CommentModel.query.get_or_404(str(comment_id))
        
        jwt_identity = get_jwt_identity()
        if jwt_identity != comment.user_id:
            abort(403, message="Access forbidden.")
        comment.content = comment_data["content"]
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the comment.")
        return comment
