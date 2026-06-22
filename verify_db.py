from db_connection import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    
    print('[OK] Database connection successful!')
    print('\nAvailable tables:')
    for t in tables:
        print(f'  - {list(t.values())[0]}')
    
    cursor.execute('DESCRIBE users')
    users_cols = cursor.fetchall()
    print('\nUsers table structure:')
    for col in users_cols:
        print(f'  {col["Field"]}: {col["Type"]}')
    
    cursor.execute('DESCRIBE recognized_faces')
    recog_cols = cursor.fetchall()
    print('\nRecognized_faces table structure:')
    for col in recog_cols:
        print(f'  {col["Field"]}: {col["Type"]}')
    
    conn.close()
    print('\n[OK] Database is ready!')
    
except Exception as e:
    print(f'[ERROR] {e}')
