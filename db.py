try:
    import mysql.connector
    from mysql.connector import Error
except Exception:
    mysql = None
    Error = Exception

from config import Config

# Realistic fallback dataset for Cloud Preview / Demo mode when MySQL is offline
DEMO_PRODUCTS = [
    {'Product_ID': 101, 'Product_Name': 'Fortune Sunflower Oil 1L', 'Category': 'Oil', 'Brand': 'Fortune', 'Purchase_Price': 125.0, 'Selling_Price': 145.0, 'Available_Quantity': 80, 'Expiry_Date': '2027-06-30'},
    {'Product_ID': 102, 'Product_Name': 'Tata Salt 1kg', 'Category': 'Grocery', 'Brand': 'Tata', 'Purchase_Price': 20.0, 'Selling_Price': 25.0, 'Available_Quantity': 150, 'Expiry_Date': '2028-12-31'},
    {'Product_ID': 103, 'Product_Name': 'Parle-G Biscuits', 'Category': 'Biscuits', 'Brand': 'Parle', 'Purchase_Price': 5.0, 'Selling_Price': 6.0, 'Available_Quantity': 200, 'Expiry_Date': '2027-08-15'},
    {'Product_ID': 104, 'Product_Name': 'Good Day Butter Cookies', 'Category': 'Biscuits', 'Brand': 'Britannia', 'Purchase_Price': 25.0, 'Selling_Price': 30.0, 'Available_Quantity': 90, 'Expiry_Date': '2027-09-20'},
    {'Product_ID': 105, 'Product_Name': 'Amul Taaza Milk 1L', 'Category': 'Dairy', 'Brand': 'Amul', 'Purchase_Price': 26.0, 'Selling_Price': 30.0, 'Available_Quantity': 60, 'Expiry_Date': '2026-10-25'},
    {'Product_ID': 106, 'Product_Name': 'Amul Butter 500g', 'Category': 'Dairy', 'Brand': 'Amul', 'Purchase_Price': 52.0, 'Selling_Price': 60.0, 'Available_Quantity': 45, 'Expiry_Date': '2027-02-28'},
    {'Product_ID': 107, 'Product_Name': 'Maggi 2-Minute Noodles', 'Category': 'Snacks', 'Brand': 'Nestle', 'Purchase_Price': 12.0, 'Selling_Price': 15.0, 'Available_Quantity': 120, 'Expiry_Date': '2027-07-31'},
    {'Product_ID': 108, 'Product_Name': 'Tata Tea Gold 250g', 'Category': 'Beverages', 'Brand': 'Tata', 'Purchase_Price': 145.0, 'Selling_Price': 165.0, 'Available_Quantity': 35, 'Expiry_Date': '2027-12-31'},
    {'Product_ID': 109, 'Product_Name': 'Nescafe Classic Coffee 50g', 'Category': 'Beverages', 'Brand': 'Nestle', 'Purchase_Price': 120.0, 'Selling_Price': 140.0, 'Available_Quantity': 25, 'Expiry_Date': '2027-11-30'},
    {'Product_ID': 110, 'Product_Name': 'Aashirvaad Shudh Chakki Atta 5kg', 'Category': 'Flour', 'Brand': 'ITC', 'Purchase_Price': 210.0, 'Selling_Price': 240.0, 'Available_Quantity': 40, 'Expiry_Date': '2027-05-31'},
    {'Product_ID': 111, 'Product_Name': 'India Gate Basmati Rice 1kg', 'Category': 'Rice', 'Brand': 'India Gate', 'Purchase_Price': 95.0, 'Selling_Price': 115.0, 'Available_Quantity': 55, 'Expiry_Date': '2028-01-31'},
    {'Product_ID': 112, 'Product_Name': 'Surf Excel Quick Wash 1kg', 'Category': 'Detergents', 'Brand': 'Surf Excel', 'Purchase_Price': 105.0, 'Selling_Price': 125.0, 'Available_Quantity': 30, 'Expiry_Date': '2028-06-30'},
    {'Product_ID': 113, 'Product_Name': 'Dove Cream Beauty Bathing Bar', 'Category': 'Personal Care', 'Brand': 'Dove', 'Purchase_Price': 42.0, 'Selling_Price': 50.0, 'Available_Quantity': 70, 'Expiry_Date': '2028-03-31'},
    {'Product_ID': 114, 'Product_Name': 'Colgate Strong Teeth 200g', 'Category': 'Personal Care', 'Brand': 'Colgate', 'Purchase_Price': 65.0, 'Selling_Price': 75.0, 'Available_Quantity': 50, 'Expiry_Date': '2028-04-30'},
    {'Product_ID': 115, 'Product_Name': 'Kissan Fresh Tomato Ketchup', 'Category': 'Sauces', 'Brand': 'Kissan', 'Purchase_Price': 85.0, 'Selling_Price': 100.0, 'Available_Quantity': 32, 'Expiry_Date': '2027-10-31'}
]

DEMO_BILLS = [
    {'Bill_ID': 301, 'Bill_Name': 'Customer 1', 'Payment_Method': 'Cash', 'Discount': 5.0, 'Total_Amount': 170.0, 'Transaction_ID': 'TXN1001', 'Total_Items': 2},
    {'Bill_ID': 302, 'Bill_Name': 'Customer 2', 'Payment_Method': 'UPI', 'Discount': 10.0, 'Total_Amount': 230.0, 'Transaction_ID': 'TXN1002', 'Total_Items': 2},
    {'Bill_ID': 303, 'Bill_Name': 'Customer 3', 'Payment_Method': 'Card', 'Discount': 0.0, 'Total_Amount': 150.0, 'Transaction_ID': 'TXN1003', 'Total_Items': 1},
    {'Bill_ID': 304, 'Bill_Name': 'Customer 4', 'Payment_Method': 'UPI', 'Discount': 15.0, 'Total_Amount': 285.0, 'Transaction_ID': 'TXN1004', 'Total_Items': 2},
    {'Bill_ID': 305, 'Bill_Name': 'Customer 5', 'Payment_Method': 'Cash', 'Discount': 0.0, 'Total_Amount': 120.0, 'Transaction_ID': 'TXN1005', 'Total_Items': 1}
]

DEMO_SUPPLIERS = [
    {'Supplier_ID': 201, 'Supplier_Name': 'Shree Ganesh Distributors', 'Address': 'Itwari, Nagpur', 'Phone_Number': '9876501001', 'Email': 'ganesh_dist@example.com', 'Supplied_Products_Count': 1},
    {'Supplier_ID': 202, 'Supplier_Name': 'Mahalaxmi Wholesale', 'Address': 'Gandhibagh, Nagpur', 'Phone_Number': '9876501002', 'Email': 'mahalaxmi@example.com', 'Supplied_Products_Count': 1},
    {'Supplier_ID': 203, 'Supplier_Name': 'Vidarbha Foods Supply', 'Address': 'Dharampeth, Nagpur', 'Phone_Number': '9876501003', 'Email': 'vidarbha_foods@example.com', 'Supplied_Products_Count': 2},
    {'Supplier_ID': 204, 'Supplier_Name': 'Fresh Dairy Suppliers', 'Address': 'Sadar, Nagpur', 'Phone_Number': '9876501004', 'Email': 'freshdairy@example.com', 'Supplied_Products_Count': 2},
    {'Supplier_ID': 205, 'Supplier_Name': 'National Grocery Traders', 'Address': 'Kalamna, Nagpur', 'Phone_Number': '9876501005', 'Email': 'national_traders@example.com', 'Supplied_Products_Count': 1}
]

DEMO_PAYMENTS = [
    {'Payment_ID': 501, 'Supplier_ID': 201, 'Supplier_Name': 'Shree Ganesh Distributors', 'Invoice_Number': 'INV-SG-8801', 'Bill_Amount': 12500.0, 'Amount_Paid': 12500.0, 'Payment_Date': '2026-10-15', 'Payment_Method': 'Bank Transfer', 'Payment_Status': 'Paid', 'Notes': 'Fortnightly oil supply settlement', 'Balance_Due': 0.0},
    {'Payment_ID': 502, 'Supplier_ID': 202, 'Supplier_Name': 'Mahalaxmi Wholesale', 'Invoice_Number': 'INV-MW-4202', 'Bill_Amount': 4500.0, 'Amount_Paid': 4500.0, 'Payment_Date': '2026-10-18', 'Payment_Method': 'UPI', 'Payment_Status': 'Paid', 'Notes': 'Tata salt bulk purchase', 'Balance_Due': 0.0},
    {'Payment_ID': 503, 'Supplier_ID': 203, 'Supplier_Name': 'Vidarbha Foods Supply', 'Invoice_Number': 'INV-VF-1090', 'Bill_Amount': 8200.0, 'Amount_Paid': 5000.0, 'Payment_Date': '2026-10-22', 'Payment_Method': 'Cheque', 'Payment_Status': 'Partial', 'Notes': 'Biscuits & confectionery delivery', 'Balance_Due': 3200.0}
]

def get_db_connection(as_role='admin'):
    """
    Connect to MySQL with a strict 2-second timeout to prevent serverless function hangs.
    """
    if mysql is None:
        return None, "MySQL connector unavailable"

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
            'database': Config.MYSQL_DB,
            'connection_timeout': 2  # Strict 2-second timeout protects Vercel serverless
        }
        if Config.MYSQL_HOST not in ['localhost', '127.0.0.1']:
            conn_kwargs['ssl_disabled'] = False

        conn = mysql.connector.connect(**conn_kwargs)
        return conn, None
    except Exception as e:
        return None, str(e)


def execute_query(query, params=None, fetch_all=True, fetch_one=False, commit=False, as_role='admin'):
    """
    Executes a query on MySQL. If the database is unreachable (e.g. initial cloud preview),
    gracefully serves fallback demo data so the page never throws a 500 error.
    """
    conn, err = get_db_connection(as_role=as_role)
    if err or not conn:
        # Fallback handling for cloud preview
        q_upper = query.upper()
        if 'FROM PRODUCT' in q_upper and fetch_all:
            return DEMO_PRODUCTS, None
        if 'FROM BILL' in q_upper and fetch_all:
            return DEMO_BILLS, None
        if 'FROM SUPPLIER_PAYMENT' in q_upper and fetch_all:
            return DEMO_PAYMENTS, None
        if 'FROM SUPPLIER' in q_upper and fetch_all:
            return DEMO_SUPPLIERS, None
        return None, f"Database Offline: {err}"

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
    except Exception as e:
        if commit and conn:
            conn.rollback()
        return None, str(e)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def test_connection():
    """Test MySQL connection with a quick 2-second timeout."""
    conn, err = get_db_connection(as_role='admin')
    if conn and conn.is_connected():
        conn.close()
        return True, True
    return err, False
