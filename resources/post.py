import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from db import db
from models import PostModel, CategoryModel, PostCategoryModel
from schemas import (
    PlainPostSchema,
    PostResponseSchema,
    PostCreationSchema,
    PostUpdateSchema,
)
from enums.roles import UserRole
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("Post", __name__, description="Operations on posts")


@blp.route("/posts")
class PostList(MethodView):
    @jwt_required()
    @blp.response(200, PostResponseSchema(many=True))
    def get(self):
        query = PostModel.query

        # Filter by category name (?category=python&category=flask)
        category_names = request.args.getlist("category")
        if category_names:
            # More efficient approach using PostCategoryModel
            # post_ids_subquery = (
            #     db.session.query(PostCategoryModel.post_id)
            #     .join(CategoryModel, PostCategoryModel.category_id == CategoryModel.id)
            #     .filter(CategoryModel.name.in_(category_names))
            #     .distinct()
            # )
            # query = query.filter(PostModel.id.in_(post_ids_subquery))

            query = query.join(PostModel.categories).filter(
                CategoryModel.name.in_(category_names)
            )

        # Filter by author_id (?author_id=some-uuid)
        author_id = request.args.get("author_id")
        if author_id:
            query = query.filter(PostModel.author_id == author_id)
            # query = query.filter_by(author_id=author_id)
        print("-------------------------------------------------------")
        print(str(query))

        # Search by title or content (?search=flask)
        search = request.args.get("q")
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    PostModel.title.ilike(search_term),
                    PostModel.content.ilike(search_term),
                )
            )

        # filter by creation date (?created_after=2023-01-01&created_before=2023-12-31)
        if request.args.get("created_after"):
            query = query.filter(
                PostModel.created_at > request.args.get("created_after")
            )

        if request.args.get("created_before"):
            query = query.filter(
                PostModel.created_at < request.args.get("created_before")
            )

        return query.all()

    @jwt_required(fresh=True)
    @blp.arguments(PostCreationSchema)
    @blp.response(201, PostResponseSchema)
    def post(self, post_data):
        category_names = post_data.pop("category_names", [])
        post = PostModel(**post_data)

        if category_names:
            categories = CategoryModel.query.filter(
                CategoryModel.name.in_(category_names)
            ).all()

            if len(categories) != len(category_names):
                abort(404, message="One or more categories not found.")

            post.categories = categories

        post.author_id = get_jwt_identity()

        try:
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the post.")

        return post, 201


@blp.route("/posts/<uuid:post_id>")
class Post(MethodView):
    # get post details by ID
    @jwt_required()
    @blp.response(200, PostResponseSchema)
    def get(self, post_id):
        post = PostModel.query.get_or_404(str(post_id))
        return post, 200

    @jwt_required(fresh=True)
    @blp.arguments(PostUpdateSchema)
    @blp.response(200, PostResponseSchema)
    def put(self, post_data, post_id):

        # Check authorization - only author or admin can update
        jwt_identity = get_jwt_identity()
        jwt = get_jwt()

        post = PostModel.query.get_or_404(str(post_id))

        if post.author_id != jwt_identity and jwt["role"] != UserRole.ADMIN.value:
            abort(
                403,
                message="Access forbidden. Only the author or admin can update this post.",
            )
        # update categories only if the field is provided in request
        if "category_names" in post_data:
            category_names = post_data.pop("category_names")

            if category_names:  # if category_names is not empty
                categories = CategoryModel.query.filter(
                    CategoryModel.name.in_(category_names)
                ).all()

                if len(categories) != len(category_names):
                    abort(404, message="One or more categories not found.")

                post.categories = categories
            else:
                # if category_names is empty, remove the categories
                post.categories = []

        # update post data
        for key, value in post_data.items():
            setattr(post, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the post.")

        return post, 200

    @jwt_required(fresh=True)
    @blp.response(204)
    def delete(self, post_id):
        post = PostModel.query.get_or_404(str(post_id))

        # Check authorization - only author or admin can delete
        jwt_identity = get_jwt_identity()
        jwt = get_jwt()

        if post.author_id != jwt_identity and jwt["role"] != UserRole.ADMIN.value:
            abort(
                403,
                message="Access forbidden. Only the author or admin can delete this post.",
            )

        try:
            db.session.delete(post)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the post.")

        return {"message": "Post deleted successfully"}, 204
