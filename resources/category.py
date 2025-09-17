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


@blp.route("/categories")
class CategoryList(MethodView):
    # get all categories
    @jwt_required()
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        return CategoryModel.query.all()

    # create category
    @jwt_required(fresh=True)
    @blp.arguments(CategorySchema)
    @blp.response(201, CategorySchema)
    def post(self, category_data):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN.value:
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
        return category


@blp.route("/categories/<uuid:category_id>")
class CategoryItem(MethodView):
    # get category details by ID
    @jwt_required()
    @blp.response(200, CategorySchema)
    def get(self, category_id):
        category = CategoryModel.query.get_or_404(str(category_id))
        return category

    # delete category
    @jwt_required(fresh=True)
    @blp.response(204)
    def delete(self, category_id):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN.value:
            abort(403, message="Access forbidden.")

        category = CategoryModel.query.get_or_404(str(category_id))
        try:
            db.session.delete(category)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the category.")
        return ""
