from dataclasses import dataclass
from typing import Optional
from werkzeug.security import check_password_hash  # <--- ВОТ ОНА, НАША СПАСИТЕЛЬНИЦА

from database.select import select_list


@dataclass
class AuthResult:
    user: Optional[dict]
    error_message: str
    status: bool


def authorize(db_config: dict, login: str, password: str, sql_provider) -> AuthResult:
    if not login or not password:
        return AuthResult(None, 'Введите логин и пароль', False)

    try:
        result, _ = select_list(db_config, sql_provider.get('auth.sql'),
                                {'login': login}) # Убрали пароль из параметров SQL
    except ValueError as err:
        return AuthResult(None, str(err), False)

    if result is None:
        return AuthResult(None, 'Ошибка при обращении к базе данных', False)
    if not result:
        return AuthResult(None, 'Неверный логин или пароль', False)
    
    user = result[0]
    
    # Проверяем хэш пароля
    if check_password_hash(user['password'], password):
        return AuthResult(user, '', True)
    else:
        return AuthResult(None, 'Неверный логин или пароль', False)