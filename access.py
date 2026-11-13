from functools import wraps

from flask import session, redirect, url_for, request, current_app, render_template


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        return redirect(url_for('bp_auth.auth_index'))
    return wrapper


def has_access(user_group: str, endpoint: str) -> bool:
    if not user_group:
        return False
        
    access = current_app.config['db_access']
    blueprint_name = endpoint.split('.')[0]

    # 1. Сначала проверяем конкретные эндпоинты (они в приоритете)
    endpoints = access.get('endpoints', {})
    if endpoint in endpoints:
        return user_group in endpoints[endpoint]

    # 2. Если эндпоинта нет в списке, проверяем доступ ко всему блюпринту
    blueprints = access.get('blueprints', {})
    if blueprint_name in blueprints:
        return user_group in blueprints[blueprint_name]

    return False


def group_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('bp_auth.auth_index'))
        if has_access(session.get('user_group'), request.endpoint):
            return func(*args, **kwargs)
        return render_template('access_denied.html'), 403
    return wrapper
