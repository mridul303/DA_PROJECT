from contextlib import contextmanager

import pytest
from flask import template_rendered, current_app

import get_root
from flaskr import create_app
from flaskr.cassandraClass import CassandraModules

# Creating a app globally here as current_app doesn't give the appropriate
# response we want when calling the template_used() function.
app = create_app()


def init_db():
    db = CassandraModules()
    db('user')
    db.execute_query("DELETE FROM user WHERE username = 'RandomUser1234'")


@pytest.fixture(scope="module")
def client():
    init_db()
    app.config['TESTING'] = True
    app.config['USERNAME'] = "RandomUser1234"
    app.config['PASSWORD'] = "RandomPassword1234"
    with app.test_client() as client:
        with app.app_context():
            yield client


@contextmanager
def template():
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def template_used():
    """Retrun the template being rendered by the current response"""
    with template():
        yield template
