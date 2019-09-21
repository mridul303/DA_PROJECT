#TODO write docstrings for this API
import functools

from flask import (Blueprint, flash, g, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from .backend import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error=None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db

        if error is None:
            data = {'username' : username, 'password' :
                    generate_password_hash(password)}
            db.insert(data)
            return redirect(url_for('auth.login'))
        
        flash(error)

return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(f"SELECT * FROM user WHERE username = {username}")
        
        if user is None:
            error = 'Incorrect Username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

    flash(error)

return render_template('aut/login.html')

bp.before_app_requests()
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(f"SELECT * FROM user WHERE id = {user_id}")
