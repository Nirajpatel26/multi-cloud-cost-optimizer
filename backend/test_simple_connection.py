import psycopg2

# Simple connection test with new container
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = '127.0.0.1'
DB_PORT = '5433'
DB_NAME = 'cost_optimizer'

try:
    print(f"Connecting to PostgreSQL...")
    print(f"  Host: {DB_HOST}:{DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {DB_USER}")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    print("\nSUCCESS: Connection works!")
    
    # Test a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\nPostgreSQL version: {version[0][:60]}...")
    
    # Test creating a table
    cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR);")
    print("Table created successfully!")
    
    cursor.close()
    conn.close()
    
    print("\nREADY: Database is ready for mock service test!")
    
except Exception as e:
    print(f"\nERROR: Connection failed: {e}")
