import os
from datetime import date
from flask import Blueprint, render_template, request, current_app, redirect, url_for
from access import group_required
from database.sql_provider import SQLProvider
from database.select import select_list
from database.modify import modify_db

blueprint_business = Blueprint('bp_business', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_business.route('/', methods=['GET', 'POST'])
@group_required  # Защита авторизацией (Требование ЛР3)
def create_waybill():
    db_config = current_app.config['db_config']
    
    # Функция для загрузки справочников (чтобы не дублировать код)
    def get_dictionaries():
        clients, _ = select_list(db_config, "SELECT contract_num AS id, client_name AS name FROM client")
        vehicles, _ = select_list(db_config, "SELECT vehicle_id AS id, brand || ' (' || reg_number || ')' AS name FROM vehicle")
        staff, _ = select_list(db_config, "SELECT staff_id AS id, surname AS name FROM staff")
        cargos, _ = select_list(db_config, "SELECT cargo_id AS id, cargo_name AS name FROM cargo")
        return clients, vehicles, staff, cargos

    # GET-запрос: показываем пустую форму
    if request.method == 'GET':
        clients, vehicles, staff, cargos = get_dictionaries()
        return render_template('business_form.html', 
                               clients=clients, vehicles=vehicles, staff=staff, cargos=cargos)
    
    # POST-запрос: сохраняем данные
    try:
        # 1. Получаем данные из формы
        contract_num = request.form.get('contract_num')
        vehicle_id = request.form.get('vehicle_id')
        forwarder_id = request.form.get('forwarder_id')
        cargo_id = request.form.get('cargo_id')
        quantity = int(request.form.get('quantity', 0))
        
        # 2. Валидация (Исключения)
        if not all([contract_num, vehicle_id, forwarder_id, cargo_id]) or quantity <= 0:
            raise ValueError("Заполните все поля и укажите количество больше нуля")

        # 3. Создаем заголовок накладной (INSERT)
        waybill_id = modify_db(db_config, provider.get('insert_waybill.sql'), {
            'date': date.today(), 
            'contract_num': contract_num, 
            'vehicle_id': vehicle_id, 
            'forwarder_id': forwarder_id
        })

        # 4. Добавляем груз (INSERT)
        modify_db(db_config, provider.get('insert_item.sql'), {
            'waybill_id': waybill_id, 
            'cargo_id': cargo_id, 
            'quantity': quantity
        })

        # 5. Пересчитываем вес (UPDATE)
        modify_db(db_config, provider.get('update_weight.sql'), {'waybill_id': waybill_id})

        # 6. Успех — рендерим страницу успеха
        return render_template('business_success.html', waybill_id=waybill_id)

    except Exception as e:
        # Обработка исключений (вывод ошибки на форму)
        clients, vehicles, staff, cargos = get_dictionaries()
        return render_template('business_form.html', 
                               clients=clients, vehicles=vehicles, staff=staff, cargos=cargos,
                               error_message=str(e))