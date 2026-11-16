import os

from flask import Blueprint, render_template, request, session, redirect, url_for, current_app

from database.sql_provider import SQLProvider
from bp_auth.model import authorize

blueprint_auth = Blueprint('bp_auth', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_auth.route('/', methods=['GET', 'POST'])
def auth_index():
    if request.method == 'GET':
        return render_template('auth.html', error_message='', login='')

    login = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()
    result = authorize(current_app.config['db_config'], login, password, provider)

    if not result.status:
        return render_template('auth.html', error_message=result.error_message, login=login)

    session.clear()
    session['user_id'] = result.user['user_id']
    
    session['user_group'] = result.user['user_group']
    
    session.permanent = True
    return redirect(url_for('main_menu'))
