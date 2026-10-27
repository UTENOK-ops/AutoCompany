from functools import wraps

from flask import session, redirect, url_for, request, current_app, render_template


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        # не авторизован - отправляем на форму входа
        return redirect(url_for('bp_auth.auth_index'))
    return wrapper


def has_access(user_group: str, endpoint: str) -> bool:
    access = current_app.config['db_access']
    allowed = access.get(user_group, [])
    blueprint_name = endpoint.split('.')[0]
    return blueprint_name in allowed or endpoint in allowed


def group_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('bp_auth.auth_index'))
        if has_access(session.get('user_group'), request.endpoint):
            return func(*args, **kwargs)
        return render_template('access_denied.html'), 403
    return wrapper
