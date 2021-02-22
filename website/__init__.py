from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# from .secret_key import SECRET_KEY
import os

db = SQLAlchemy(app)
DB_NAME = "aircraft_database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", None)
    # app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgres://cqnjuhzztzxozx:710bd51c7319105c98c2f9d8f7430b2c1ab9400bad0c33f12978133d6da4d317@ec2-63-34-97-163.eu-west-1.compute.amazonaws.com:5432/d28ogknce5g596"
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Aircraft

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Database created ...")
