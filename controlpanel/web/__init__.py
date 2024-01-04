from flask import Flask
from web.db import db, migrate
from web.models import *

from web.pages import blueprints as page_blueprints
from web.api import blueprints as api_blueprints
from web.commands import blueprints as command_blueprints



def create_app(config=None):
    app = Flask(__name__, static_url_path='', static_folder='static')

    if config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(config)

    blueprints = page_blueprints + api_blueprints + command_blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    db.init_app(app)
    migrate.init_app(app, db)
    return app
