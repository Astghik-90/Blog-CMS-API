import os
import requests
from flask import request, render_template, current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)


from db import db
from models import UserModel
from schemas import (
    UserSchema,
    UserSignupSchema,
    UserLoginSchema,
    UpdateProfileSchema,
    ChangePasswordSchema,
    ChangeRoleSchema,
    PostResponseSchema,
)
from enums.roles import UserRole
from blocklist import BLOCKLIST
from tasks import send_user_registration_email

blp = Blueprint("Users", __name__, description="Operations on users")


# registration
@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSignupSchema)
    def post(self, user_data):

        user = UserModel(
            username=user_data["username"].lower(),
            email=user_data["email"].lower(),
            password_hash=generate_password_hash(
                user_data["password"], method="pbkdf2:sha256", salt_length=16
            ),
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Username or email already exists.")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while registering the user.")

        # send email to the user
        try:
            current_app.queue.enqueue(
                send_user_registration_email, user.email, user.username
            )
            return {
                "message": "User created successfully. Please check your email for details."
            }, 201

        except Exception as e:
            print(f"Email failed: {str(e)}")

        return {"message": "User created successfully."}, 201


# login
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data["username"]).first()

        if user and check_password_hash(user.password_hash, user_data["password"]):
            access_token = create_access_token(
                identity=str(user.id), additional_claims={"role": user.role}, fresh=True
            )
            refresh_token = create_refresh_token(
                identity=str(user.id), additional_claims={"role": user.role}
            )
            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid credentials.")


@blp.route("/refresh")
class UserRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}, 200


# get all users - only Admin can access
@blp.route("/users")
class UserList(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN.value:
            abort(403, message="Access forbidden.")
        return UserModel.query.all()


@blp.route("/users/<uuid:user_id>")
class UserProfile(MethodView):
    # get user details
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):

        jwt_identity = get_jwt_identity()
        jwt = get_jwt()

        if jwt_identity != str(user_id) and jwt["role"] != UserRole.ADMIN.value:
            abort(403, message="Access forbidden.")

        user = UserModel.query.get_or_404(str(user_id))
        return user

    # update profile info
    @jwt_required(fresh=True)
    @blp.arguments(UpdateProfileSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        jwt_identity = get_jwt_identity()
        # error if trying to update another user's profile
        if str(user_id) != jwt_identity:
            abort(403, message="Access forbidden.")

        user = UserModel.query.get_or_404(str(user_id))

        # Check for existing username and email
        existing_user = UserModel.query.filter(
            or_(
                and_(
                    UserModel.username == user_data["username"].lower(),
                    UserModel.id != user_id,
                ),
                and_(
                    UserModel.email == user_data["email"].lower(),
                    UserModel.id != user_id,
                ),
            )
        ).first()

        if existing_user:
            if existing_user.username == user_data["username"].lower():
                abort(409, message="Username already taken.")
            if existing_user.email == user_data["email"].lower():
                abort(409, message="Email already registered.")

        try:
            user.username = user_data["username"].lower()
            user.email = user_data["email"].lower()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

        return user

    # delete user
    @jwt_required(fresh=True)
    @blp.response(204)
    def delete(self, user_id):
        jwt_identity = get_jwt_identity()
        jwt = get_jwt()

        if jwt_identity != str(user_id) and jwt["role"] != UserRole.ADMIN.value:
            abort(403, message="Access forbidden.")

        user = UserModel.query.get_or_404(str(user_id))
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the user.")
        return {"message": "User deleted successfully"}


# change password
@blp.route("/users/<uuid:user_id>/password")
class UserPasswordChange(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ChangePasswordSchema)
    def patch(self, password_data, user_id):
        # check the identity of the user
        jwt_identity = get_jwt_identity()
        if jwt_identity != str(user_id):
            abort(403, message="Access forbidden.")

        user = UserModel.query.get_or_404(str(user_id))
        # error if the password is wrong
        if not check_password_hash(user.password_hash, password_data["old_password"]):
            abort(401, message="Invalid old password.")

        user.password_hash = generate_password_hash(
            password_data["new_password"], method="pbkdf2:sha256", salt_length=16
        )
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while changing the password.")

        return {"message": "Password changed successfully."}, 200


# change user role
@blp.route("/users/<uuid:user_id>/role")
class UserRoleChange(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ChangeRoleSchema)
    @blp.response(200, UserSchema)
    def patch(self, role_data, user_id):
        jwt = get_jwt()
        if jwt["role"] != UserRole.ADMIN.value:
            abort(403, message="Access forbidden.")

        user = UserModel.query.get_or_404(str(user_id))
        user.role = role_data["role"]
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the user role.")

        return user


# get posts o
@blp.route("/users/<uuid:user_id>/posts")
class UserPosts(MethodView):
    @jwt_required()
    @blp.response(200, PostResponseSchema(many=True))
    def get(self, user_id):
        user = UserModel.query.get_or_404(str(user_id))
        return user.posts
