from flask import Flask
from flask_cors import CORS

from app.models.models import User, Friendship, Blog
from app.extensions.extensions import db, swagger, mail

from app.functions.account import account_bp
from app.functions.blog import blog_bp
from app.functions.email_funcs import email_bp
from app.functions.timer import timer_bp
from app.functions.search_api import search_bp
from app.functions.chat import chat_bp
from app.functions.checklist import checklist_bp
from app.functions.health_aid import health_aid_bp

from app.config import configs


def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(configs[config_name])

    # blueprints
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(email_bp, url_prefix='/email')
    app.register_blueprint(timer_bp, url_prefix='/timer')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(checklist_bp, url_prefix='/checklist')
    app.register_blueprint(health_aid_bp, url_prefix='/healthAid')

    # init_extensions
    db.init_app(app)
    swagger.init_app(app)
    mail.init_app(app)

    return app
