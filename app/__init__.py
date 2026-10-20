from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lydo.db'
    app.config['SECRET_KEY'] = 'dev-secret-key'

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    # user loader for flask-login
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all() # Creates tables based on models.py

    return app