import psycopg

try:
    conn = psycopg.connect(conninfo="dbname=lawyer_db user=postgres password=postgres host=localhost port=5432")
    print("Successfully connected to PostgreSQL database")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print("PostgreSQL version:", cursor.fetchone())
except Exception as e:
    print("Connection failed:", e)
