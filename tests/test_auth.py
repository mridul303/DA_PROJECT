import pytest
from flask import current_app, template_rendered

import get_root


def register(client, username, password):
    return client.post("/auth/register", data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def test_registeration(client, template_used):
    # Test if a message is flashed if username or password field is empty and
    # the register page is re-rendered
    with template_used() as templates:
        # When username field is empty
        response = register(
            client,
            "",
            current_app.config['PASSWORD']
            )
        assert response.status_code == 200
        assert b'Username is required.' in response.data
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'auth/register.html'

        # When password field is empty
        response = register(
            client,
            current_app.config['PASSWORD'],
            ""
            )
        assert response.status_code == 200
        assert b'Password is required.' in response.data
        assert len(templates) == 2
        template, context = templates[1]
        assert template.name == 'auth/register.html'

    # After a successful first time registration, the login.html is rendered
    # and passed as response. We use signals provided by blinker and flask in
    # order to get the name of the template which was rendered.
    with template_used() as templates:
        response = register(
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
        response = register(
            client,
            current_app.config['USERNAME'],
            current_app.config['PASSWORD']
            )
        assert response.status_code == 200
        assert b'Username alreay exists.' in response.data
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'auth/register.html'


def login(client, username, password):
    return client.post("/auth/login", data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def test_login(client, template_used):
    with template_used() as templates:
        # Test for incorrect username.
        response = login(
            client,
            current_app.config['USERNAME'] + 'someRandomVal',
            current_app.config['PASSWORD']
            )
        assert response.status_code == 200
        assert len(templates) == 1
        assert b'Incorrect Username.' in response.data
        template, context = templates[0]
        assert template.name == 'auth/login.html'

        # Test for password.
        response = login(
            client,
            current_app.config['USERNAME'],
            current_app.config['PASSWORD'] + 'someRandomVal'
            )
        assert response.status_code == 200
        assert len(templates) == 2
        assert b'Incorrect Password.' in response.data
        template, context = templates[1]
        assert template.name == 'auth/login.html'

    # Write tests for successful login
