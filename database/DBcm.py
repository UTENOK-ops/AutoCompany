"""Контекстный менеджер для работы с базой данных PostgreSQL."""
import psycopg2
from psycopg2 import OperationalError


class DBContextManager:
    """
    Открывает соединение и курсор при входе в блок with
    и корректно закрывает их при выходе.

    with DBContextManager(db_config) as cursor:
        cursor.execute(sql)
    """

    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            return self.cursor
        except OperationalError as err:
            print('Ошибка подключения к БД:', err)
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn is None:
            return False
        if exc_type:
            print('Ошибка при работе с БД:', exc_val)
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
        # True - исключение обработано и дальше не пробрасывается
        return True
