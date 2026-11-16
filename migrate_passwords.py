import json
import os
import psycopg2
from werkzeug.security import generate_password_hash

# Загружаем настройки БД
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'data_files', 'db_config.json'), encoding='utf-8') as f:
    db_config = json.load(f)

def migrate_passwords():
    print("Запуск миграции паролей...")
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Получаем всех пользователей
        cursor.execute("SELECT user_id, login, password FROM internal_user")
        users = cursor.fetchall()
        
        updated_count = 0
        for user_id, login, password in users:
            # Если пароль не начинается с маркеров хэша (scrypt или pbkdf2), значит он открытый
            if not password.startswith(('scrypt:', 'pbkdf2:')):
                new_hash = generate_password_hash(password)
                cursor.execute(
                    "UPDATE internal_user SET password = %s WHERE user_id = %s",
                    (new_hash, user_id)
                )
                print(f"Пароль пользователя '{login}' успешно зашифрован.")
                updated_count += 1
            else:
                print(f"Пароль пользователя '{login}' уже зашифрован. Пропуск.")
                
        conn.commit()
        print(f"\nМиграция завершена! Обновлено паролей: {updated_count}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при миграции: {e}")

if __name__ == '__main__':
    migrate_passwords()