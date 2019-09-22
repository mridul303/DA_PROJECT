import os

from flask import Flask

def create_app(test_config=None):
    """An Application Factory to create and configure the flask app

       NOTE: Don't publish the actual SECRET_KEY when commiting
       the code to github!!
    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except:
        pass

    @app.route('/hello')
    def hello():
        return "Hello, World!"

    from . import backend
    backend.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
