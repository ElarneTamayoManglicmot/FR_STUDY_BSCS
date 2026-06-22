import pymysql

# Connect to thesis database
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='thesis'
    )
    cursor = conn.cursor()
    
    # Read and execute schema
    with open('schema.sql', 'r') as f:
        sql_commands = f.read().split(';')
        
    for command in sql_commands:
        command = command.strip()
        if command:
            try:
                cursor.execute(command)
                print(f"Executed: {command[:50]}...")
            except Exception as e:
                print(f"Error: {e}")
    
    conn.commit()
    
    # Verify tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("\nTables created:")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    print("\nDatabase setup complete!")
    
except Exception as e:
    print(f"Error: {e}")
