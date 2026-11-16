import json
import os
import redis
from flask import Flask, render_template, session
from flask_session import Session
from extensions import cache  # Импортируем кэш из отдельного файла

from access import login_required, has_access
from bp_auth.route import blueprint_auth
from bp_query.route import blueprint_query
from bp_report.route import blueprint_report
from bp_business.route import blueprint_business
from database.select import select_list


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'transport_company_secret_key')

# ================= НАСТРОЙКА REDIS =================
# 1. Настройка кэша (база 0)
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0?protocol=2'
app.config['CACHE_DEFAULT_TIMEOUT'] = 600
cache.init_app(app)

# 2. Настройка сессий (база 1)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379/1', protocol=2)
app.config['SESSION_KEY_PREFIX'] = 'autocompany:'
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_PERMANENT'] = False
Session(app)
# ===================================================

# Загрузка конфигов
with open(os.path.join(BASE_DIR, 'data_files', 'db_config.json'), encoding='utf-8') as f:
    app.config['db_config'] = json.load(f)
with open(os.path.join(BASE_DIR, 'data_files', 'db_access.json'), encoding='utf-8') as f:
    app.config['db_access'] = json.load(f)

# Регистрация блюпринтов
app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_query, url_prefix='/query')
app.register_blueprint(blueprint_report, url_prefix='/report')
app.register_blueprint(blueprint_business, url_prefix='/business')

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

@app.context_processor
def inject_user_info():
    user_name = None
    # Если пользователь авторизован (есть user_id в сессии)
    if 'user_id' in session:
        try:
            # Ищем его ФИО в базе по ID
            res, _ = select_list(app.config['db_config'], 
                                 "SELECT full_name FROM internal_user WHERE user_id = %(id)s", 
                                 {'id': session['user_id']})
            if res:
                user_name = res[0]['full_name']
        except Exception:
            pass
    return dict(user_name=user_name)
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)