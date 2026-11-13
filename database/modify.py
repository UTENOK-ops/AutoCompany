from database.DBcm import DBContextManager

def modify_db(db_config: dict, sql: str, params: dict = None):
    """Выполняет INSERT/UPDATE/DELETE. Возвращает ID добавленной записи (для INSERT)."""
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Не удалось подключиться к базе данных')
        
        cursor.execute(sql, params or {})
        
        # Если был INSERT с RETURNING, возвращаем ID новой записи
        if cursor.description is not None:
            return cursor.fetchone()[0]
        return True