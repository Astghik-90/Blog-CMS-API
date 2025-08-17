from flask import request
from flask.views import MethodView
from enums.roles import UserRole
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import CategoryModel
from schemas import CategorySchema

blp = Blueprint("Category", __name__, description="Operations on categories")

@blp.route("/category")
class CategoryList(MethodView):
    @jwt_required()
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        return CategoryModel.query.all(), 200

    @jwt_required()
    @blp.arguments(CategorySchema)
    @blp.response(201, CategorySchema)
    def post(self, category_data):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN:
            abort(403, message="Access forbidden.")
            
        category = CategoryModel(**category_data)
        try:
            db.session.add(category)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="A category with this name already exists.")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the category.")
        return category, 201

@blp.route("/category/<uuid:category_id>")
class CategoryItem(MethodView):
    @jwt_required()
    @blp.response(200, CategorySchema)
    def get(self, category_id):
        # Convert UUID object to string for database query
        category = CategoryModel.query.get_or_404(str(category_id))
        return category, 200

    @jwt_required()
    @blp.arguments(CategorySchema)
    @blp.response(200, CategorySchema)
    def put(self, category_data, category_id):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN:
            abort(403, message="Access forbidden.")
            
        # Convert UUID object to string for database query
        category = CategoryModel.query.get_or_404(str(category_id))
        category.name = category_data["name"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="A category with this name already exists.")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the category.")
        return category, 200

    @jwt_required()
    @blp.response(204)
    def delete(self, category_id):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN:
            abort(403, message="Access forbidden.")
            
        # Convert UUID object to string for database query
        category = CategoryModel.query.get_or_404(str(category_id))
        try:
            db.session.delete(category)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the category.")
        return "", 204
