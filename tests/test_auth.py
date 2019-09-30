from contextlib import contextmanager

import pytest
from flask import current_app, template_rendered

import get_root
from flaskr import cassandraClass


def login(client, username, password):
    return client.post("/auth/register", data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def test_registeration(client, template_used):
    # After a successful first time registration, the login.html is rendered
    # and passed as response. We use signals provided by blinker and flask in
    # order to get the name of the template which was rendered.
    with template_used() as templates:
        response = login(
            client,
            current_app.config['USERNAME'],
            current_app.config['PASSWORD']
            )
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'auth/login.html'

    # An already registered user should flash an error message saying
    # 'Username alreay exists.' and re-render the register.html page
    with template_used() as templates:
        response = login(
            client,
            current_app.config['USERNAME'],
            current_app.config['PASSWORD']
            )
        assert response.status_code == 200
        assert b'Username alreay exists.' in response.data
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'auth/register.html'