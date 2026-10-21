"""Blueprint «Авторизация» внутренних пользователей."""
import os

from flask import Blueprint, render_template, request, session, redirect, url_for, current_app

from database.sql_provider import SQLProvider
from bp_auth.model import authorize

blueprint_auth = Blueprint('bp_auth', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_auth.route('/', methods=['GET', 'POST'])
def auth_index():
    # GET - выдать форму ввода логина и пароля
    if request.method == 'GET':
        return render_template('auth.html', error_message='', login='')

    # POST - проверить логин и пароль
    login = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()
    result = authorize(current_app.config['db_config'], login, password, provider)

    if not result.status:
        return render_template('auth.html', error_message=result.error_message, login=login)

    # сохраняем параметры пользователя в сессии и передаём управление в главное меню
    session['user_id'] = result.user['user_id']
    session['login'] = result.user['login']
    session['user_group'] = result.user['user_group']
    session['full_name'] = result.user['full_name']
    session.permanent = True
    return redirect(url_for('main_menu'))
