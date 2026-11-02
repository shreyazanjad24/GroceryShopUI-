import mysql.connector
from mysql.connector import Error
from flask import session, current_app
from config import Config

def get_db_connection(as_role='admin'):
    """
    Connect to MySQL database with the specified credentials.
    Defaults to admin (root) so the shopkeeper has full access to INSERT, UPDATE, DELETE.
    """
    if as_role == 'viewer':
        user = Config.MYSQL_VIEWER_USER
        password = Config.MYSQL_VIEWER_PASSWORD
    else:
        user = Config.MYSQL_ADMIN_USER
        password = Config.MYSQL_ADMIN_PASSWORD

    try:
        conn_kwargs = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': user,
            'password': password,
            'database': Config.MYSQL_DB
        }
        # If connecting to a cloud database (not localhost), support SSL connections
        if Config.MYSQL_HOST not in ['localhost', '127.0.0.1']:
            conn_kwargs['ssl_disabled'] = False

        conn = mysql.connector.connect(**conn_kwargs)
        return conn, None
    except Error as e:
        return None, str(e)


def execute_query(query, params=None, fetch_all=True, fetch_one=False, commit=False, as_role='admin'):
    """
    Executes a query and returns (result, error_message).
    When commit=True, it permanently commits the changes to MySQL database.
    """
    conn, err = get_db_connection(as_role=as_role)
    if err:
        return None, f"Database Connection Error: {err}"

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if commit:
            conn.commit()
            affected = cursor.rowcount
            return affected, None

        if fetch_one:
            result = cursor.fetchone()
            return result, None

        if fetch_all:
            result = cursor.fetchall()
            return result, None

        return True, None
    except Error as e:
        if commit and conn:
            conn.rollback()
        return None, str(e)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def test_connection():
    """Test MySQL connection with admin credentials."""
    conn, err = get_db_connection(as_role='admin')
    if conn and conn.is_connected():
        conn.close()
        return True, True
    return err, False
