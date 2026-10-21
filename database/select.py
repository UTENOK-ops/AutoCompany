"""Выполнение SELECT-запросов к БД (work_with_db)."""
from database.DBcm import DBContextManager


def select_list(db_config: dict, sql: str, params: dict = None):
    """
    Выполняет запрос и возвращает (список словарей, список имён столбцов).
    Если соединение с БД не удалось - возвращает (None, None).
    """
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Не удалось подключиться к базе данных')
        cursor.execute(sql, params or {})
        schema = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(schema, row)) for row in rows], schema
    return None, None
