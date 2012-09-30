# -*- encoding:utf-8 -*-
import logging
from logging.handlers import WatchedFileHandler

from flask import Flask
from flask.ext.assets import Environment, Bundle


def create_app():
    from server.views.frontend import frontend as blueprint_frontend
    from server.views.entry import entry as blueprint_entry
    from server.views.filter import filter as blueprint_filter
    from server.views.pinboard import pinboard as blueprint_pinboard
    from server.db import db
    from server.login import login_manager

    app = Flask(__name__, instance_relative_config=True)
    app.jinja_options = dict(app.jinja_options)
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

    app.config.from_pyfile("default_settings.py")
    app.config.from_envvar('PINBOARD_SETTINGS', silent=True)

    if not app.debug:
        file_handler = WatchedFileHandler(app.config.get("LOG_FILENAME",
            "pinboard.log"))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    assets = Environment(app)

    js_assets = Bundle(
            "scripts/jquery-1.7.2.js",
            "scripts/jquery-ui-1.8.16.custom.min.js",
            #"scripts/chosen.jquery.min.js",
            "scripts/bootstrap.min.js",
            "scripts/angular-1.0.1.js",
            #"scripts/angular-cookies-1.0.0.js",
            #"scripts/taffy.js",
            "scripts/sugar-1.2.4.min.js",
            #"scripts/jquery.couch.js",
            Bundle("lib/*.coffee", filters=["coffeescript", ]),
            filters=["rjsmin", ],
            output="generated_app.js",
            )
    css_assets = Bundle(
            "stylesheets/jquery-ui-1.8.16.custom.css",
            Bundle(
                "stylesheets/app.less",
                filters=["less", ],
                ),
            filters=["cssmin", ],
            output="generated_app.css",
            )
    assets.register('js_all', js_assets)
    assets.register('css_all', css_assets)

    db.init_app(app)
    login_manager.setup_app(app)

    app.register_blueprint(blueprint_frontend)
    app.register_blueprint(blueprint_entry, url_prefix="/entry")
    app.register_blueprint(blueprint_filter, url_prefix="/filter")
    app.register_blueprint(blueprint_pinboard, url_prefix="/pinboards")

    return app
