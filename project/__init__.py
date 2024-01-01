from flask import Flask
from models import db
import os


def create_app():
    app = Flask(__name__)
    from . import views
    from models import db

    app.register_blueprint(views.bp)

    # Configuration settings for the database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"  # SQLite example
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.urandom(24)

    # Initialize the database extension with the app
    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
