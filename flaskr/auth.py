# TODO INVESTIGATE/FIX: the @bp.before_app_request stores the session even
# after a browser restart or in some cases after code restarts!!
#
# TODO write docstrings for this API
#
# TODO either use prepared statements or validate input before using it as
#      queries as regular statements might be prone to injection attacks!

import functools
import uuid

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from .backend import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db('user')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute_query(f"SELECT * FROM user WHERE username = '{username}'").one() is not None:
            error = 'Username alreay exists.'

        if error is None:
            data = {'username': username, 'password':
                    generate_password_hash(password), 'id': uuid.uuid4()}
            db.insert(data)
            # Redirect to login URL after successful reggistration
            return redirect(url_for('auth.login'))

        flash(error)

    # Return back to the registeration page in case of an error
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db('user')
        error = None
        user = db.execute_query(f"SELECT * FROM user WHERE username = '{username}'").one()

        if user is None:
            error = 'Incorrect Username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # Redirect to the user's index page on successful login
            return redirect(url_for('index'))

        flash(error)

    # Return back to the login page in case of an error
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """Run this function before any request to check if user is already logged
    in by checking the session id. Set the app context data based on weather
    they are logged in or not.
    """
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db('session')
        g.user = db.execute_query(f"SELECT * FROM session WHERE id = {user_id}").one()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
