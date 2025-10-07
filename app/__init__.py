from flask import Flask
from app.models import db
from app.routes_api import api
from app.routes_admin import admin
from flask_bcrypt import Bcrypt
import os

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "indotex-key")

    # Handle Railway's postgres:// to postgresql:// scheme for SQLAlchemy
    raw_db_url = os.environ.get("DATABASE_URL", "sqlite:///license.db")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    bcrypt.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(admin)

    @app.route("/")
    def root():
        return "Indotex License Server + Admin Panel (Railway) ✅"

    with app.app_context():
        db.create_all()

    return app
