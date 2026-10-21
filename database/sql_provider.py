"""SQL-провайдер: загружает тексты SQL-запросов из .sql файлов."""
import os


class SQLProvider:
    """
    Читает все .sql файлы из каталога и хранит их по имени файла.
    Параметры подставляются не здесь, а драйвером БД
    (плейсхолдеры вида %(name)s) - это защищает от SQL-инъекций.
    """

    def __init__(self, file_path: str):
        self.scripts = {}
        for file_name in os.listdir(file_path):
            if file_name.endswith('.sql'):
                with open(os.path.join(file_path, file_name), encoding='utf-8') as f:
                    self.scripts[file_name] = f.read()

    def get(self, file_name: str) -> str:
        return self.scripts[file_name]
