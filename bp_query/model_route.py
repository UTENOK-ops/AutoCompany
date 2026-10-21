"""Модель варианта использования «Работа с запросами»."""
from dataclasses import dataclass, field
from typing import Optional

from database.select import select_list


@dataclass
class QueryResult:
    result: list = field(default_factory=list)
    error_message: str = ''
    status: bool = False


def model_route(db_config: dict, sql: str, params: Optional[dict] = None) -> QueryResult:
    """Выполняет SQL-запрос и упаковывает результат для контроллера."""
    try:
        result, _ = select_list(db_config, sql, params)
    except ValueError as err:
        return QueryResult(error_message=str(err))
    if result is None:
        return QueryResult(error_message='Ошибка при выполнении запроса к базе данных')
    return QueryResult(result=result, status=True)
