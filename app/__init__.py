import os

from flask import Flask

from app import db
from app.routes import bp


def create_app(config=None):
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "expenses.db")
    if config:
        app.config.update(config)
    db.init_app(app)
    app.register_blueprint(bp)
    return app
