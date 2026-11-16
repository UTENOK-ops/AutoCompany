from database.DBcm import DBContextManager
from database.select import select_list

def get_dictionaries(db_config, provider):
    """Загрузка справочников для формы"""
    clients, _ = select_list(db_config, provider.get('get_clients.sql'))
    vehicles, _ = select_list(db_config, provider.get('get_vehicles.sql'))
    staff, _ = select_list(db_config, provider.get('get_staff.sql'))
    cargos, _ = select_list(db_config, provider.get('get_cargos.sql'))
    return clients, vehicles, staff, cargos

def create_waybill_transaction(db_config, provider, data):
    """Создание накладной в ОДНОЙ транзакции"""
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError("Не удалось подключиться к базе данных")
        
        try:
            # 1. Создаем накладную
            cursor.execute(provider.get('insert_waybill.sql'), data)
            waybill_id = cursor.fetchone()[0]
            
            # 2. Добавляем груз
            cursor.execute(provider.get('insert_item.sql'), {
                'waybill_id': waybill_id, 
                'cargo_id': data['cargo_id'], 
                'quantity': data['quantity']
            })
            
            # 3. Обновляем вес
            cursor.execute(provider.get('update_weight.sql'), {'waybill_id': waybill_id})
            
            return waybill_id
        except Exception as e:
            # Ошибка автоматически вызовет rollback в DBContextManager (мы починили его в п.1)
            raise ValueError(f"Ошибка БД: {e}")