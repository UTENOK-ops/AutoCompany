import json
import os

from flask import Flask, render_template, session, redirect, url_for

from access import login_required, has_access
from bp_auth.route import blueprint_auth
from bp_query.route import blueprint_query
from bp_report.route import blueprint_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = 'transport_company_secret_key'

with open(os.path.join(BASE_DIR, 'data_files', 'db_config.json'), encoding='utf-8') as f:
    app.config['db_config'] = json.load(f)
with open(os.path.join(BASE_DIR, 'data_files', 'db_access.json'), encoding='utf-8') as f:
    app.config['db_access'] = json.load(f)

app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_query, url_prefix='/query')
app.register_blueprint(blueprint_report, url_prefix='/report')

# функция доступна во всех шаблонах: прятать недоступные пункты меню
app.jinja_env.globals['has_access'] = lambda endpoint: has_access(session.get('user_group'), endpoint)

GROUP_NAMES = {
    'director': 'Директор',
    'dispatcher': 'Диспетчер',
    'manager': 'Менеджер по работе с клиентами',
}
app.jinja_env.globals['group_names'] = GROUP_NAMES


@app.route('/')
@login_required
def main_menu():
    return render_template('main_menu.html')


@app.route('/exit')
def exit_system():
    session.clear()
    return render_template('exit.html')


@app.errorhandler(404)
def page_not_found(_):
    return render_template('message.html', title='Страница не найдена',
                           message='Такой страницы нет в системе.'), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
