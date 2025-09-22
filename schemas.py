from marshmallow import Schema, fields, validate
from datetime import datetime


# user schemas
class UserSchema(Schema):  # for get users details
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserSignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, load_only=True)
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Regexp(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
            error="Password must be at least 8 characters long and include letters and numbers.",
        ),
    )


class UserLoginSchema(Schema):
    username_email = fields.Str(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)


class UpdateProfileSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)


class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Regexp(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
            error="Password must be at least 8 characters long and include letters and numbers.",
        ),
    )


class ChangeRoleSchema(Schema):
    role = fields.Int(required=True, validate=lambda x: x in [1, 2])


# comment schema
class CommentSchema(Schema):
    id = fields.Str(dump_only=True)
    content = fields.Str(required=True, validate=validate.Length(min=2))
    user_id = fields.Str(dump_only=True)
    post_id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


# category schema
class CategorySchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


# post schemas
class PostSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    category_names = fields.List(fields.Str(), required=False)


class PostResponseSchema(PostSchema):  # post details
    id = fields.Str()
    title = fields.Str()
    content = fields.Str()
    author_id = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    categories = fields.List(fields.Nested(CategorySchema))
