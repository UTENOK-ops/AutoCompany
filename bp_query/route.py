"""Blueprint «Работа с запросами»."""
import os
from datetime import date

from flask import Blueprint, render_template, request, current_app

from access import group_required
from database.sql_provider import SQLProvider
from bp_query.model_route import model_route

blueprint_query = Blueprint('bp_query', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


def run(sql_file: str, params: dict = None):
    return model_route(current_app.config['db_config'], provider.get(sql_file), params)


def show_form(query: dict, error_message: str = '', values: dict = None):
    return render_template('query_form.html', query=query,
                           error_message=error_message, values=values or {})


def show_result(query: dict, rows: list, subtitle: str = ''):
    if not rows:
        return show_form(query, 'По заданным условиям ничего не найдено', request.form)
    return render_template('query_result.html', query=query, rows=rows, subtitle=subtitle)


# Описание запросов: заголовок, поля формы и столбцы таблицы результата.
# Шаблоны query_form.html и query_result.html строятся по этому описанию.
QUERIES = {
    'clients_by_zone': {
        'title': 'Клиенты по району (МКАД)',
        'description': 'Список клиентов в пределах или за пределами МКАД.',
        'fields': [{'name': 'zone', 'label': 'Район', 'type': 'select',
                    'options': [('all', 'Все клиенты'), ('inside', 'В пределах МКАД'),
                                ('outside', 'За пределами МКАД')]}],
        'columns': [('contract_num', '№ договора'), ('client_name', 'Название'),
                    ('address', 'Адрес'), ('zone', 'Район'),
                    ('contact_surname', 'Контактное лицо'), ('contact_phone', 'Телефон')],
    },
    'waybills_by_period': {
        'title': 'Накладные за период',
        'description': 'Товарно-транспортные накладные с датой перевозки в заданном диапазоне.',
        'fields': [{'name': 'date_from', 'label': 'Дата с', 'type': 'date'},
                   {'name': 'date_to', 'label': 'Дата по', 'type': 'date'}],
        'columns': [('waybill_id', '№ накладной'), ('waybill_date', 'Дата'),
                    ('client_name', 'Клиент-отправитель'), ('vehicle', 'Транспорт'),
                    ('forwarder', 'Экспедитор'), ('total_weight', 'Общий вес, кг')],
    },
    'waybill_items': {
        'title': 'Состав накладной',
        'description': 'Список перевезённых грузов и их количество по номеру накладной.',
        'fields': [{'name': 'waybill_id', 'label': 'Номер накладной', 'type': 'number',
                    'min': 1, 'step': 1}],
        'columns': [('cargo_name', 'Груз'), ('quantity', 'Количество'),
                    ('avg_weight', 'Средний вес, кг'), ('item_weight', 'Вес позиции, кг')],
    },
    'vehicles_by_capacity': {
        'title': 'Автомобили по грузоподъёмности',
        'description': 'Автомобили с грузоподъёмностью не меньше заданной и число их рейсов.',
        'fields': [{'name': 'min_capacity', 'label': 'Грузоподъёмность от, т', 'type': 'number',
                    'min': 0, 'step': 0.5}],
        'columns': [('reg_number', 'Рег. номер'), ('brand', 'Марка'),
                    ('release_year', 'Год выпуска'), ('capacity', 'Грузоподъёмность, т'),
                    ('trips', 'Рейсов')],
    },
    'staff_by_position': {
        'title': 'Сотрудники по должности',
        'description': 'Персонал фирмы выбранной должности со стажем на должности.',
        'fields': [{'name': 'position', 'label': 'Должность', 'type': 'select', 'options': []}],
        'columns': [('surname', 'Фамилия'), ('address', 'Адрес'),
                    ('birth_date', 'Дата рождения'), ('position', 'Должность'),
                    ('hire_date', 'Дата зачисления'), ('experience', 'Стаж, лет')],
    },
    'client_year_weight': {
        'title': 'Вес грузов клиентов с начала года',
        'description': 'Нарастающий итог веса перевезённых грузов и положенная скидка (диаграмма).',
        'fields': [],
        'columns': [],
    },
}


@blueprint_query.route('/')
@group_required
def query_menu():
    queries = [(name, q['title'], q['description']) for name, q in QUERIES.items()]
    return render_template('query_menu.html', queries=queries)


@blueprint_query.route('/clients', methods=['GET', 'POST'])
@group_required
def clients_by_zone():
    query = QUERIES['clients_by_zone']
    if request.method == 'GET':
        return show_form(query)
    zone = request.form.get('zone', '')
    if zone not in ('all', 'inside', 'outside'):
        return show_form(query, 'Выберите район из списка')
    res = run('clients_by_zone.sql', {'zone': zone})
    if not res.status:
        return show_form(query, res.error_message)
    return show_result(query, res.result)


@blueprint_query.route('/waybills', methods=['GET', 'POST'])
@group_required
def waybills_by_period():
    query = QUERIES['waybills_by_period']
    if request.method == 'GET':
        return show_form(query)
    try:
        date_from = date.fromisoformat(request.form.get('date_from', ''))
    except ValueError:
        return show_form(query, 'Неверно введена начальная дата', request.form)
    try:
        date_to = date.fromisoformat(request.form.get('date_to', ''))
    except ValueError:
        return show_form(query, 'Неверно введена конечная дата', request.form)
    if date_from > date_to:
        return show_form(query, 'Начальная дата больше конечной', request.form)
    res = run('waybills_by_period.sql', {'date_from': date_from, 'date_to': date_to})
    if not res.status:
        return show_form(query, res.error_message, request.form)
    return show_result(query, res.result,
                       f'с {date_from:%d.%m.%Y} по {date_to:%d.%m.%Y}')


@blueprint_query.route('/waybill-items', methods=['GET', 'POST'])
@group_required
def waybill_items():
    query = QUERIES['waybill_items']
    if request.method == 'GET':
        return show_form(query)
    waybill_id = request.form.get('waybill_id', '')
    if not waybill_id.isdigit():
        return show_form(query, 'Номер накладной должен быть целым положительным числом',
                         request.form)
    header = run('waybill_header.sql', {'waybill_id': int(waybill_id)})
    if not header.status:
        return show_form(query, header.error_message, request.form)
    if not header.result:
        return show_form(query, f'Накладной № {waybill_id} не существует', request.form)
    items = run('waybill_items.sql', {'waybill_id': int(waybill_id)})
    if not items.status:
        return show_form(query, items.error_message, request.form)
    h = header.result[0]
    return render_template('query_result.html', query=query, rows=items.result,
                           subtitle=f'Накладная № {h["waybill_id"]} от {h["waybill_date"]}',
                           header=h)


@blueprint_query.route('/vehicles', methods=['GET', 'POST'])
@group_required
def vehicles_by_capacity():
    query = QUERIES['vehicles_by_capacity']
    if request.method == 'GET':
        return show_form(query)
    try:
        min_capacity = float(request.form.get('min_capacity', '').replace(',', '.'))
        if min_capacity < 0:
            raise ValueError
    except ValueError:
        return show_form(query, 'Грузоподъёмность должна быть неотрицательным числом',
                         request.form)
    res = run('vehicles_by_capacity.sql', {'min_capacity': min_capacity})
    if not res.status:
        return show_form(query, res.error_message, request.form)
    return show_result(query, res.result, f'грузоподъёмность от {min_capacity:g} т')


@blueprint_query.route('/staff', methods=['GET', 'POST'])
@group_required
def staff_by_position():
    query = dict(QUERIES['staff_by_position'])
    positions = run('positions.sql')
    if not positions.status:
        return show_form(query, positions.error_message)
    options = [(p['position'], p['position']) for p in positions.result]
    query['fields'] = [dict(query['fields'][0], options=options)]

    if request.method == 'GET':
        return show_form(query)
    position = request.form.get('position', '')
    if position not in [o[0] for o in options]:
        return show_form(query, 'Такой должности нет', request.form)
    res = run('staff_by_position.sql', {'position': position})
    if not res.status:
        return show_form(query, res.error_message, request.form)
    return show_result(query, res.result, position)


@blueprint_query.route('/year-weight')
@group_required
def client_year_weight():
    query = QUERIES['client_year_weight']
    res = run('client_year_weight.sql')
    if not res.status:
        return render_template('message.html', title=query['title'],
                               message=res.error_message)
    rows = res.result
    max_weight = max((float(r['year_weight']) for r in rows), default=0) or 1
    total = sum(float(r['year_weight']) for r in rows)
    return render_template('year_weight_chart.html', query=query, rows=rows,
                           max_weight=max_weight, total=total, year=date.today().year)
