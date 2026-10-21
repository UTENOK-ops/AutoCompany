# ИС «Автотранспортная компания» (вариант 15)

Flask + PostgreSQL + HTML/CSS. Лабораторные работы по курсу «Разработка информационных систем».

## Структура проекта

```
transport_company/
├── app.py                    # точка входа: главное меню, регистрация blueprint'ов
├── access.py                 # декораторы login_required и group_required (ЛР2)
├── requirements.txt
├── data_files/
│   ├── db_config.json        # параметры подключения к PostgreSQL
│   └── db_access.json        # словарь доступа: группа -> разрешённые варианты использования
├── database/
│   ├── DBcm.py               # контекстный менеджер соединения с БД
│   ├── sql_provider.py       # загрузка SQL-запросов из .sql файлов
│   └── select.py             # выполнение SELECT (work_with_db)
├── bp_auth/                  # blueprint «Авторизация» (ЛР2)
│   ├── route.py  model.py  sql/auth.sql  templates/auth.html
├── bp_query/                 # blueprint «Работа с запросами»
│   ├── route.py  model_route.py  sql/*.sql  templates/*.html
├── bp_report/                # blueprint «Работа с отчётами» (заготовка, только директор)
├── templates/                # base, main_menu, exit, access_denied, message
├── static/style.css
└── sql/
    ├── 01_create_tables.sql  # таблицы, ограничения, триггер нарастающего итога
    └── 02_fill_data.sql      # тестовые данные и пользователи ИС
```

## Запуск в PyCharm

1. Откройте папку `transport_company` в PyCharm (File → Open), создайте виртуальное окружение
   (Settings → Project → Python Interpreter → Add Interpreter → Virtualenv).
2. В терминале PyCharm: `pip install -r requirements.txt`
3. Создайте базу в PostgreSQL (pgAdmin или psql):
   ```
   CREATE DATABASE transport_company;
   ```
   и выполните в ней по очереди `sql/01_create_tables.sql` и `sql/02_fill_data.sql`
   (в pgAdmin: Query Tool → открыть файл → F5; в psql: `\i sql/01_create_tables.sql`).
4. Впишите свой пароль от PostgreSQL в `data_files/db_config.json`.
5. Запустите `app.py` (правой кнопкой → Run 'app') и откройте http://127.0.0.1:5001

## Пользователи

| Логин | Пароль | Группа | Что доступно |
|---|---|---|---|
| director | director123 | Директор | все запросы, отчёты |
| dispatcher | dispatcher123 | Диспетчер | запросы 2–5 (накладные, транспорт, персонал) |
| manager | manager123 | Менеджер по работе с клиентами | запросы 1, 2, 3, 6 (клиенты, накладные, диаграмма) |

Права задаются в `data_files/db_access.json`. Элемент списка может быть именем blueprint'а целиком
(`"bp_query"`) или отдельного обработчика (`"bp_query.clients_by_zone"`).

## Запросы

1. Клиенты в пределах / за пределами МКАД.
2. Накладные за период дат.
3. Состав накладной (грузы и количество) по её номеру.
4. Автомобили с грузоподъёмностью не меньше заданной и число их рейсов.
5. Сотрудники выбранной должности со стажем.
6. Вес грузов клиентов с начала года (нарастающий итог) — горизонтальная диаграмма и скидки.

Нарастающий итог `client.year_weight` поддерживается триггером `trg_waybill_year_weight`:
при добавлении, изменении или удалении накладной текущего года вес клиента пересчитывается.
Тестовые накладные датированы 2025–2026 годами, поэтому скрипт заполнения нужно выполнять в 2026 году
(иначе нарастающий итог «с начала года» будет нулевым — это корректное поведение).
