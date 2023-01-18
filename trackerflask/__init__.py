import os

from flask import Flask, g

from . import db, auth, trackapp


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_envvar("TRACKAPP_SETTINGS")
        app.config["DATABASE"] = os.path.join(app.instance_path, app.config["DATABASE"])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    db.init_app(app)

    app.register_blueprint(auth.bp)

    app.register_blueprint(trackapp.bp)
    app.add_url_rule('/', endpoint='index')

    return app