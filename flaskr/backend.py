
import click
from flask import current_app, g
from flask.cli import with_appcontext

from .cassandraClass import CassandraModules


# The following code(enclosed within the multiline comment) is used if you want
# to intialize the database with certain values, properties, table, etc.
# You can use it, for example, to initialize the tables you would be using in
# your project when you deploy the app for the first time. 
# To use it, run the command:
#
#                            flask init-db
#
# The code has been commented out as after the intial use, you probably will
# not be using the command again.
# If you want to use it uncomment the init_db() and init_db_command() functions
# and also the app.cli.add_command() line in the function init_app()

# def init_db():
#     db = get_db()
#     db.execute_query("TRUNCATE user")
#
# @click.command('init-db')
# @with_appcontext
# def init_db_command():
#     init_db()
#     click.echo("Connected to database")


def init_app(app):
    """This function is used to register the current flask app with the
    app.teardown_appcontext(). The teardown_appcontext() method is called
    everytime the app instance is cleaning up after returning the response.
    """
    app.teardown_appcontext(close_db)

    """The following line of code has been intentionally commented out. Read the
    above to undersand why.
    """
    #app.cli.add_command(init_db_command)


def get_db(table):
    """Create a database object db using the application context 'g'.
    This function also ensures that multiple call from the same
    flask app will use the same connection to the database instead
    of creating a new one everytime.

    Here 'db' is an object of the cassandraModules class and not
    an actual database connection. The connection is handled by the 
    class.
    """
    if 'db' not in g:
        g.db = CassandraModules()
        g.db(table)


    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.closeConnection()
