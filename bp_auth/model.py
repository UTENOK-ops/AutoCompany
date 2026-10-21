"""Модель варианта использования «Авторизация»."""
from dataclasses import dataclass
from typing import Optional

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
                                {'login': login, 'password': password})
    except ValueError as err:
        return AuthResult(None, str(err), False)

    if result is None:
        return AuthResult(None, 'Ошибка при обращении к базе данных', False)
    if not result:
        return AuthResult(None, 'Неверный логин или пароль', False)
    return AuthResult(result[0], '', True)
