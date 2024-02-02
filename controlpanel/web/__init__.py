from flask import Flask
from web.db import db, migrate
from web.models import *

from web.pages import blueprints as page_blueprints
from web.api import blueprints as api_blueprints
from web.commands import blueprints as command_blueprints
import datetime


def create_app(config=None):
    app = Flask(__name__, static_url_path='', static_folder='static')

    if config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(config)

    blueprints = page_blueprints + api_blueprints + command_blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    register_filters(app)

    db.init_app(app)
    migrate.init_app(app, db)
    return app


def register_filters(app):
    @app.template_filter('verbose_near_date')
    def verbose_near_date_filter(d: datetime.datetime):
        now = datetime.datetime.now().date()
        date = d.date()
        if date == now:
            verbdate = 'Today'
        elif date == now - datetime.timedelta(days=1):
            verbdate = 'Yesterday'
        else:
            verbdate = d.strftime('%d/%m/%Y')

        return verbdate + ' at ' + d.strftime('%I:%M %p')
