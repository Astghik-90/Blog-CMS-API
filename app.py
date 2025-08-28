import os
import redis
from rq import Queue

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from db import db 
from blocklist import BLOCKLIST

from resources.user import blp as UserBlueprint
from resources.post import blp as PostBlueprint
from resources.category import blp as CategoryBlueprint
from resources.comment import blp as CommentBlueprint

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    connection = redis.from_url(os.getenv("REDIS_URL"))
    app.queue = Queue("emails", connection=connection)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Blog CMS API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-this-super-secret-key-in-production")
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"msg": "Token revoked."}, 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            "description": "The token is not fresh.", 
            "error": "fresh_token_required"
        }), 401


    api.register_blueprint(UserBlueprint)
    api.register_blueprint(PostBlueprint)
    api.register_blueprint(CategoryBlueprint)
    api.register_blueprint(CommentBlueprint)
    return app
