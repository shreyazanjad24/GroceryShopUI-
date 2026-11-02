import mysql.connector
from config import Config
import os

def initialize_database():
    print("=" * 60)
    print("Initializing GroceryShopDB in MySQL...")
    print(f"Connecting to MySQL Host: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    print(f"User: {Config.MYSQL_ADMIN_USER}")
    print("=" * 60)

    # 1. Connect without selecting database first
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_ADMIN_USER,
            password=Config.MYSQL_ADMIN_PASSWORD
        )
        cursor = conn.cursor()
        print("[SUCCESS] Connected to MySQL Server!")
    except Exception as e:
        print(f"[ERROR] Could not connect to MySQL server: {e}")
        print("Please check your MySQL root password in config.py or verify MySQL is running.")
        return False

    # 2. Read SQL file
    sql_path = os.path.join(os.path.dirname(__file__), 'database', 'GroceryShopDB.sql')
    if not os.path.exists(sql_path):
        print(f"[ERROR] SQL file not found at: {sql_path}")
        return False

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split statements carefully
    statements = sql_content.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        # Skip DELIMITER and empty statements
        if not stmt or stmt.startswith('--') or stmt.startswith('DELIMITER') or stmt == '//':
            continue
        try:
            cursor.execute(stmt)
        except Exception as e:
            # Skip procedure or trigger drop warnings
            if 'DROP' not in stmt.upper():
                print(f"[WARNING] Statement notice: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print("[SUCCESS] GroceryShopDB schema, tables, records, views, and users configured!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    initialize_database()

