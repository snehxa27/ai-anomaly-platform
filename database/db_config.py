import psycopg2

DB_CONFIG = {
    "dbname": "ai_anomaly_db",
    "user": "sneha",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful")
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None


if __name__ == "__main__":
    connection = get_connection()
    if connection:
        connection.close()
        print("Connection closed.")