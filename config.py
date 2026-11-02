import os

class Config:
    # Secret key for Flask session
    SECRET_KEY = os.environ.get('SECRET_KEY', 'grocery_store_secret_key_12345')

    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_DB = os.environ.get('MYSQL_DB', 'GroceryShopDB')

    # 1. Admin Credentials (Full Privileges: DDL, DML, DCL)
    # CHANGE THIS to your MySQL root password:
    MYSQL_ADMIN_USER = os.environ.get('MYSQL_ADMIN_USER', 'root')
    MYSQL_ADMIN_PASSWORD = os.environ.get('Shreya@1234', 'root')

    # 2. Restricted Viewer Credentials (Only SELECT on Views & Product Table)
    MYSQL_VIEWER_USER = os.environ.get('MYSQL_VIEWER_USER', 'grocery_viewer')
    MYSQL_VIEWER_PASSWORD = os.environ.get('MYSQL_VIEWER_PASSWORD', 'Grocery@123')

