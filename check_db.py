import pymysql

# Connect without specifying database
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password=''
    )
    cursor = conn.cursor()
    
    # Show all databases
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print("Available databases:")
    for db in databases:
        print(f"  - {db[0]}")
    
    # Check if 'thesis' exists
    cursor.execute("SHOW DATABASES LIKE 'thesis'")
    result = cursor.fetchone()
    
    if not result:
        print("\n'thesis' database not found. Creating it...")
        cursor.execute("CREATE DATABASE thesis")
        print(" - Database 'thesis' created successfully!")
    else:
        print("\n - Database 'thesis' already exists!")
    
    cursor.close()
    conn.close()
    print("\nDatabase check complete!")
    
except Exception as e:
    print(f"Error: {e}")
