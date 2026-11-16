import os
from datetime import date
from flask import Blueprint, render_template, request, current_app, redirect, url_for
from access import group_required
from database.sql_provider import SQLProvider
from bp_business.model import get_dictionaries, create_waybill_transaction
from flask import Blueprint, render_template, request, current_app, redirect, url_for

blueprint_business = Blueprint('bp_business', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_business.route('/', methods=['GET', 'POST'])
@group_required
def create_waybill():
    db_config = current_app.config['db_config']
    
    if request.method == 'GET':
        try:
            clients, vehicles, staff, cargos = get_dictionaries(db_config, provider)
            return render_template('business_form.html', clients=clients, vehicles=vehicles, staff=staff, cargos=cargos)
        except Exception as e:
            return render_template('message.html', title="Ошибка", message=f"Сервер БД недоступен: {e}")
    
    try:
        contract_num = request.form.get('contract_num')
        vehicle_id = request.form.get('vehicle_id')
        forwarder_id = request.form.get('forwarder_id')
        cargo_id = request.form.get('cargo_id')
        quantity_str = request.form.get('quantity', '0')
        
        if not quantity_str.isdigit() or int(quantity_str) <= 0:
            raise ValueError("Количество должно быть целым положительным числом")
            
        if not all([contract_num, vehicle_id, forwarder_id, cargo_id]):
            raise ValueError("Заполните все поля")

        data = {
            'date': date.today(), 
            'contract_num': contract_num, 
            'vehicle_id': vehicle_id, 
            'forwarder_id': forwarder_id,
            'cargo_id': cargo_id,
            'quantity': int(quantity_str)
        }

        waybill_id = create_waybill_transaction(db_config, provider, data)
        
        current_app.extensions['cache'].delete('year_weight_data')

        return redirect(url_for('bp_business.waybill_created', waybill_id=waybill_id))

    except ValueError as e:
        clients, vehicles, staff, cargos = get_dictionaries(db_config, provider)
        return render_template('business_form.html', clients=clients, vehicles=vehicles, staff=staff, cargos=cargos, error_message=str(e))

@blueprint_business.route('/success/<int:waybill_id>')
@group_required
def waybill_created(waybill_id):
    return render_template('business_success.html', waybill_id=waybill_id)