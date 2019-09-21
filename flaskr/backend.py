from .cassandraClass import CassandraModules

import click
from flask import current_app, g
from flask.cli import with_appcontext

def init_db():
    db = get_db()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Connected to database")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_db(table="xyz"):
    """Create a database object db using the application context 'g'.

       Here 'db' is an object of the cassandraModules class and not
       an actual database connection. The connection is handled by the 
       class.
    """
    if 'db' not in g:
        g.db = CassandraModules(table)

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.closeConnection()
