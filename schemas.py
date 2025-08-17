from marshmallow import Schema, fields, validate
from datetime import datetime
    
# plain schemas
class PlainCommentSchema(Schema):
    id = fields.Str(dump_only=True)
    content = fields.Str(required=True)
    author = fields.Str(dump_only=True)
    
class PlainPostSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)

class PlainUserSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    
class CategorySchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
 
#user schemas   
class UserSchema(PlainUserSchema): # for get users details
    email = fields.Email(required=True)
    role = fields.Int(required=True, dump_only=True) 
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
class UserSignupSchema(PlainUserSchema):
    email = fields.Email(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True, 
                          validate=validate.Regexp(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
            error="Password must be at least 8 characters long and include letters and numbers."
        ))
    
class UserLoginSchema(Schema):
    username = fields.Str(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)

class UpdateProfileSchema(PlainUserSchema):
    email = fields.Email(required=True)
    role = fields.Int(required=True, dump_only=True, validate=lambda x: x in [1, 2]) 
    updated_at = fields.DateTime(dump_only=True)

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, load_only=True, validate=validate.Regexp(
        r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
        error="Password must be at least 8 characters long and include letters and numbers."
    ))

class ChangeRoleSchema(Schema):
    role = fields.Int(required=True, validate=lambda x: x in [1, 2])

# comment schemas
class CommentSchema(PlainCommentSchema):
    post = fields.Nested(PlainPostSchema(), dump_only=True)
    author_id = fields.Str(required=True, load_only=True)

# post schemas   
class PostUpdateSchema(Schema):
    title = fields.Str()
    content = fields.Str()
    categories = fields.List(fields.Nested(CategorySchema))

class PostCreationSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    category_names = fields.List(fields.Str(), dump_default=[])

class PostResponseSchema(PlainPostSchema): #individual post details
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    author = fields.Nested(PlainUserSchema())
    comments = fields.List(fields.Nested(PlainCommentSchema()), dump_default=[])
    categories = fields.List(fields.Nested(CategorySchema), dump_default=[])


