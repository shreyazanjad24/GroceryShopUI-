from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from db import get_db_connection, execute_query, test_connection
import json
import random
import datetime

app = Flask(__name__)
app.config.from_object(Config)

def init_tables():
    """Ensure SUPPLIER_PAYMENT table exists in MySQL."""
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS SUPPLIER_PAYMENT (
            Payment_ID INT PRIMARY KEY,
            Supplier_ID INT,
            Invoice_Number VARCHAR(50),
            Bill_Amount DECIMAL(10,2) NOT NULL,
            Amount_Paid DECIMAL(10,2) NOT NULL,
            Payment_Date DATE,
            Payment_Method VARCHAR(30),
            Payment_Status VARCHAR(20) DEFAULT 'Paid',
            Notes VARCHAR(200),
            FOREIGN KEY (Supplier_ID) REFERENCES SUPPLIER(Supplier_ID) ON DELETE CASCADE
        );
    """
    execute_query(create_table_sql, commit=True, as_role='admin')

    # Seed sample supplier payments if table is empty
    count_res, _ = execute_query("SELECT COUNT(*) AS total FROM SUPPLIER_PAYMENT", fetch_one=True, as_role='admin')
    if count_res and count_res['total'] == 0:
        seed_sql = """
            INSERT INTO SUPPLIER_PAYMENT VALUES
            (501, 201, 'INV-SG-8801', 12500.00, 12500.00, '2026-10-15', 'Bank Transfer', 'Paid', 'Fortnightly oil supply settlement'),
            (502, 202, 'INV-MW-4202', 4500.00, 4500.00, '2026-10-18', 'UPI', 'Paid', 'Tata salt bulk purchase'),
            (503, 203, 'INV-VF-1090', 8200.00, 5000.00, '2026-10-22', 'Cheque', 'Partial', 'Biscuits & confectionery delivery (bal 3200)'),
            (504, 204, 'INV-FD-3312', 6400.00, 6400.00, '2026-10-25', 'UPI', 'Paid', 'Dairy butter & milk supply'),
            (505, 207, 'INV-RF-7741', 15800.00, 0.00, '2026-10-28', 'Bank Transfer', 'Pending', 'Atta & detergent wholesale consignment');
        """
        for stmt in seed_sql.strip().split(';'):
            if stmt.strip():
                execute_query(stmt.strip(), commit=True, as_role='admin')

# -------------------------------------------------------------
# 1. SHOPKEEPER DASHBOARD & DATA VISUALIZATION
# -------------------------------------------------------------
@app.route('/')
def index():
    admin_status, _ = test_connection()
    if admin_status is True:
        try:
            init_tables()
        except Exception:
            pass

    stats = {
        'total_revenue': 0.0,
        'inventory_value': 0.0,
        'total_products': 0,
        'total_bills': 0,
        'low_stock_count': 0
    }
    
    chart_category_labels = []
    chart_category_stock = []
    chart_category_values = []
    chart_payment_labels = []
    chart_payment_totals = []
    top_products_labels = []
    top_products_values = []
    low_stock_items = []
    recent_bills = []

    if admin_status is True:
        # 1. High-level KPIs
        rev_row, _ = execute_query("SELECT IFNULL(SUM(Total_Amount),0) AS total_revenue, COUNT(*) AS total_bills FROM BILL", fetch_one=True, as_role='admin')
        if rev_row:
            stats['total_revenue'] = float(rev_row['total_revenue'])
            stats['total_bills'] = rev_row['total_bills']

        stock_row, _ = execute_query("SELECT COUNT(*) AS total_products, IFNULL(SUM(Selling_Price * Available_Quantity),0) AS total_val FROM PRODUCT", fetch_one=True, as_role='admin')
        if stock_row:
            stats['total_products'] = stock_row['total_products']
            stats['inventory_value'] = float(stock_row['total_val'])

        low_row, _ = execute_query("SELECT COUNT(*) AS count FROM PRODUCT WHERE Available_Quantity < 40", fetch_one=True, as_role='admin')
        if low_row:
            stats['low_stock_count'] = low_row['count']

        # 2. Data Visualization 1: Stock by Category
        cat_data, _ = execute_query("""
            SELECT Category, 
                   SUM(Available_Quantity) AS total_stock,
                   ROUND(SUM(Selling_Price * Available_Quantity), 2) AS category_value
            FROM PRODUCT 
            GROUP BY Category 
            ORDER BY total_stock DESC
        """, as_role='admin')
        if cat_data:
            chart_category_labels = [row['Category'] for row in cat_data]
            chart_category_stock = [int(row['total_stock']) for row in cat_data]
            chart_category_values = [float(row['category_value']) for row in cat_data]

        # 3. Data Visualization 2: Sales by Payment Method
        pay_data, _ = execute_query("""
            SELECT Payment_Method, 
                   COUNT(*) AS count, 
                   IFNULL(SUM(Total_Amount), 0) AS total_sales
            FROM BILL 
            GROUP BY Payment_Method
        """, as_role='admin')
        if pay_data:
            chart_payment_labels = [row['Payment_Method'] for row in pay_data]
            chart_payment_totals = [float(row['total_sales']) for row in pay_data]

        # 4. Data Visualization 3: Top Value Inventory Products
        top_data, _ = execute_query("""
            SELECT Product_Name, (Selling_Price * Available_Quantity) AS total_value
            FROM PRODUCT
            ORDER BY total_value DESC
            LIMIT 5
        """, as_role='admin')
        if top_data:
            top_products_labels = [row['Product_Name'] for row in top_data]
            top_products_values = [float(row['total_value']) for row in top_data]

        # 5. Low Stock Warning Table (< 40 units)
        low_stock_items, _ = execute_query("""
            SELECT Product_ID, Product_Name, Category, Brand, Available_Quantity, Selling_Price
            FROM PRODUCT
            WHERE Available_Quantity < 40
            ORDER BY Available_Quantity ASC
            LIMIT 6
        """, as_role='admin')

        # 6. Recent Sales/Bills
        recent_bills, _ = execute_query("""
            SELECT Bill_ID, Bill_Name, Payment_Method, Total_Amount, Transaction_ID
            FROM BILL
            ORDER BY Bill_ID DESC
            LIMIT 5
        """, as_role='admin')

    return render_template(
        'index.html',
        stats=stats,
        admin_status=admin_status,
        cat_labels=json.dumps(chart_category_labels),
        cat_stock=json.dumps(chart_category_stock),
        cat_values=json.dumps(chart_category_values),
        pay_labels=json.dumps(chart_payment_labels),
        pay_totals=json.dumps(chart_payment_totals),
        top_labels=json.dumps(top_products_labels),
        top_values=json.dumps(top_products_values),
        low_stock_items=low_stock_items or [],
        recent_bills=recent_bills or []
    )

# -------------------------------------------------------------
# 2. INVENTORY & PRODUCT MANAGEMENT (CRUD)
# -------------------------------------------------------------
@app.route('/products')
def products():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'id')

    query = "SELECT * FROM PRODUCT WHERE 1=1"
    params = []

    if search:
        query += " AND (Product_Name LIKE %s OR Brand LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        query += " AND Category = %s"
        params.append(category)

    if sort == 'price_high':
        query += " ORDER BY Selling_Price DESC"
    elif sort == 'price_low':
        query += " ORDER BY Selling_Price ASC"
    elif sort == 'stock_low':
        query += " ORDER BY Available_Quantity ASC"
    elif sort == 'name':
        query += " ORDER BY Product_Name ASC"
    else:
        query += " ORDER BY Product_ID ASC"

    product_list, err = execute_query(query, params=params, fetch_all=True, as_role='admin')

    categories_raw, _ = execute_query("SELECT DISTINCT Category FROM PRODUCT ORDER BY Category", as_role='admin')
    categories = [row['Category'] for row in categories_raw] if categories_raw else []

    return render_template(
        'products.html',
        products=product_list or [],
        categories=categories,
        search=search,
        selected_category=category,
        sort=sort,
        error=err
    )

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            p_id = int(request.form['product_id'])
            p_name = request.form['product_name'].strip()
            category = request.form['category'].strip()
            brand = request.form['brand'].strip()
            purchase_price = float(request.form['purchase_price'])
            selling_price = float(request.form['selling_price'])
            quantity = int(request.form['available_quantity'])
            expiry_date = request.form['expiry_date']

            insert_sql = """
                INSERT INTO PRODUCT (Product_ID, Product_Name, Category, Brand, Purchase_Price, Selling_Price, Available_Quantity, Expiry_Date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (p_id, p_name, category, brand, purchase_price, selling_price, quantity, expiry_date)
            
            _, err = execute_query(insert_sql, params=params, commit=True, as_role='admin')
            if err:
                flash(f"Database Error: {err}", "danger")
            else:
                flash(f"Product '{p_name}' successfully added to database inventory!", "success")
                return redirect(url_for('products'))
        except Exception as ex:
            flash(f"Invalid input: {str(ex)}", "danger")

    next_id_res, _ = execute_query("SELECT IFNULL(MAX(Product_ID), 100) + 1 AS next_id FROM PRODUCT", fetch_one=True, as_role='admin')
    suggested_id = next_id_res['next_id'] if next_id_res else 101

    return render_template('product_form.html', action='Add', product=None, suggested_id=suggested_id)

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        try:
            p_name = request.form['product_name'].strip()
            category = request.form['category'].strip()
            brand = request.form['brand'].strip()
            purchase_price = float(request.form['purchase_price'])
            selling_price = float(request.form['selling_price'])
            quantity = int(request.form['available_quantity'])
            expiry_date = request.form['expiry_date']

            update_sql = """
                UPDATE PRODUCT
                SET Product_Name = %s, Category = %s, Brand = %s,
                    Purchase_Price = %s, Selling_Price = %s,
                    Available_Quantity = %s, Expiry_Date = %s
                WHERE Product_ID = %s
            """
            params = (p_name, category, brand, purchase_price, selling_price, quantity, expiry_date, product_id)

            _, err = execute_query(update_sql, params=params, commit=True, as_role='admin')
            if err:
                flash(f"Database Error: {err}", "danger")
            else:
                flash(f"Product '{p_name}' updated successfully in database!", "success")
                return redirect(url_for('products'))
        except Exception as ex:
            flash(f"Invalid input: {str(ex)}", "danger")

    product, err = execute_query("SELECT * FROM PRODUCT WHERE Product_ID = %s", params=(product_id,), fetch_one=True, as_role='admin')
    if err or not product:
        flash(f"Product not found: {err or ''}", "danger")
        return redirect(url_for('products'))

    return render_template('product_form.html', action='Edit', product=product, suggested_id=product_id)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    delete_sql = "DELETE FROM PRODUCT WHERE Product_ID = %s"
    _, err = execute_query(delete_sql, params=(product_id,), commit=True, as_role='admin')
    if err:
        flash(f"Database Error during deletion: {err}", "danger")
    else:
        flash(f"Product ID #{product_id} deleted permanently from database!", "success")
    return redirect(url_for('products'))

@app.route('/products/adjust-stock/<int:product_id>', methods=['POST'])
def adjust_stock(product_id):
    delta = int(request.form.get('delta', 0))
    if delta != 0:
        sql = "UPDATE PRODUCT SET Available_Quantity = GREATEST(0, Available_Quantity + %s) WHERE Product_ID = %s"
        _, err = execute_query(sql, params=(delta, product_id), commit=True, as_role='admin')
        if err:
            flash(f"Error updating stock: {err}", "danger")
        else:
            flash(f"Stock adjusted ({'+' if delta > 0 else ''}{delta}) for Product #{product_id}!", "info")
    return redirect(request.referrer or url_for('products'))

# -------------------------------------------------------------
# 3. SALES & CUSTOMER BILLING (POS - Add Customer Bill)
# -------------------------------------------------------------
@app.route('/bills')
def bills():
    bills_list, _ = execute_query("""
        SELECT 
            B.Bill_ID,
            B.Bill_Name,
            B.Payment_Method,
            B.Discount,
            B.Total_Amount,
            B.Transaction_ID,
            COUNT(BP.Product_ID) AS Total_Items
        FROM BILL B
        LEFT JOIN BILL_PRODUCT BP ON B.Bill_ID = BP.Bill_ID
        GROUP BY B.Bill_ID, B.Bill_Name, B.Payment_Method, B.Discount, B.Total_Amount, B.Transaction_ID
        ORDER BY B.Bill_ID DESC
    """, as_role='admin')

    items_list, _ = execute_query("""
        SELECT 
            BP.Bill_ID,
            P.Product_Name,
            P.Category,
            BP.Quantity,
            BP.Unit_Selling_Price,
            (BP.Quantity * BP.Unit_Selling_Price) AS Line_Total
        FROM BILL_PRODUCT BP
        JOIN PRODUCT P ON BP.Product_ID = P.Product_ID
        ORDER BY BP.Bill_ID DESC
    """, as_role='admin')

    items_by_bill = {}
    if items_list:
        for item in items_list:
            b_id = item['Bill_ID']
            if b_id not in items_by_bill:
                items_by_bill[b_id] = []
            items_by_bill[b_id].append(item)

    return render_template('bills.html', bills=bills_list or [], items_by_bill=items_by_bill)

@app.route('/bills/new', methods=['GET', 'POST'])
def create_bill():
    if request.method == 'POST':
        conn, err = get_db_connection(as_role='admin')
        if err or not conn:
            flash(f"Database connection error: {err}", "danger")
            return redirect(url_for('bills'))

        try:
            customer_name = request.form.get('customer_name', 'Walk-in Customer').strip()
            payment_method = request.form.get('payment_method', 'Cash')
            discount = float(request.form.get('discount', 0.0))

            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')

            if not product_ids:
                flash("Please add at least one product to the bill.", "warning")
                return redirect(url_for('create_bill'))

            cursor = conn.cursor(dictionary=True)

            # 1. Determine next Bill_ID
            cursor.execute("SELECT IFNULL(MAX(Bill_ID), 300) + 1 AS next_bill_id FROM BILL")
            next_bill_row = cursor.fetchone()
            bill_id = next_bill_row['next_bill_id']

            # 2. Generate Unique Transaction ID
            txn_id = f"TXN{random.randint(2000, 9999)}"

            # 3. Calculate line items and verify stock
            total_before_discount = 0.0
            bill_items = []

            for pid_str, qty_str in zip(product_ids, quantities):
                if not pid_str:
                    continue
                pid = int(pid_str)
                qty = int(qty_str)
                if qty <= 0:
                    continue

                cursor.execute("SELECT Product_Name, Selling_Price, Available_Quantity FROM PRODUCT WHERE Product_ID = %s", (pid,))
                prod = cursor.fetchone()
                if not prod:
                    continue

                if prod['Available_Quantity'] < qty:
                    conn.rollback()
                    flash(f"Insufficient stock for '{prod['Product_Name']}'. Available: {prod['Available_Quantity']} units, Requested: {qty}.", "danger")
                    return redirect(url_for('create_bill'))

                unit_price = float(prod['Selling_Price'])
                total_before_discount += (unit_price * qty)
                bill_items.append((bill_id, pid, qty, unit_price))

            if not bill_items:
                conn.rollback()
                flash("No valid items entered.", "warning")
                return redirect(url_for('create_bill'))

            final_total = max(0.0, total_before_discount - discount)

            # 4. Insert into BILL
            insert_bill_sql = """
                INSERT INTO BILL (Bill_ID, Bill_Name, Payment_Method, Discount, Total_Amount, Transaction_ID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_bill_sql, (bill_id, customer_name, payment_method, discount, final_total, txn_id))

            # 5. Insert into BILL_PRODUCT and decrement stock in PRODUCT
            insert_bp_sql = """
                INSERT INTO BILL_PRODUCT (Bill_ID, Product_ID, Quantity, Unit_Selling_Price)
                VALUES (%s, %s, %s, %s)
            """
            update_stock_sql = """
                UPDATE PRODUCT SET Available_Quantity = Available_Quantity - %s WHERE Product_ID = %s
            """

            for item in bill_items:
                cursor.execute(insert_bp_sql, item)
                cursor.execute(update_stock_sql, (item[2], item[1]))

            conn.commit()
            cursor.close()
            conn.close()

            flash(f"Invoice #{bill_id} generated successfully for '{customer_name}' (Total: ₹{final_total:.2f})! Stock updated in MySQL.", "success")
            return redirect(url_for('bills'))

        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            flash(f"Failed to generate bill: {str(e)}", "danger")
            return redirect(url_for('create_bill'))

    # GET: fetch available products for the dropdown picker
    products, _ = execute_query(
        "SELECT Product_ID, Product_Name, Category, Brand, Selling_Price, Available_Quantity FROM PRODUCT WHERE Available_Quantity > 0 ORDER BY Product_Name ASC",
        as_role='admin'
    )
    return render_template('bill_create.html', products=products or [])

# -------------------------------------------------------------
# 4. SUPPLIERS & SUPPLIER BILLING / PAYMENTS
# -------------------------------------------------------------
@app.route('/suppliers', methods=['GET', 'POST'])
def suppliers():
    if request.method == 'POST':
        # Add new supplier
        try:
            s_name = request.form['supplier_name'].strip()
            address = request.form['address'].strip()
            phone = request.form['phone'].strip()
            email = request.form.get('email', '').strip()

            next_s, _ = execute_query("SELECT IFNULL(MAX(Supplier_ID), 200) + 1 AS next_id FROM SUPPLIER", fetch_one=True, as_role='admin')
            s_id = next_s['next_id'] if next_s else 201

            sql = "INSERT INTO SUPPLIER (Supplier_ID, Supplier_Name, Address, Phone_Number, Email) VALUES (%s, %s, %s, %s, %s)"
            _, err = execute_query(sql, params=(s_id, s_name, address, phone, email), commit=True, as_role='admin')
            if err:
                flash(f"Error adding supplier: {err}", "danger")
            else:
                flash(f"Supplier '{s_name}' registered successfully!", "success")
                return redirect(url_for('suppliers'))
        except Exception as ex:
            flash(f"Invalid input: {str(ex)}", "danger")

    # Fetch suppliers list
    suppliers_list, _ = execute_query("""
        SELECT S.Supplier_ID, S.Supplier_Name, S.Address, S.Phone_Number, S.Email,
               COUNT(PS.Product_ID) AS Supplied_Products_Count
        FROM SUPPLIER S
        LEFT JOIN PRODUCT_SUPPLIER PS ON S.Supplier_ID = PS.Supplier_ID
        GROUP BY S.Supplier_ID, S.Supplier_Name, S.Address, S.Phone_Number, S.Email
        ORDER BY S.Supplier_ID ASC
    """, as_role='admin')

    # Fetch supplier billings and payments
    supplier_payments, _ = execute_query("""
        SELECT SP.Payment_ID, SP.Supplier_ID, S.Supplier_Name, SP.Invoice_Number,
               SP.Bill_Amount, SP.Amount_Paid, SP.Payment_Date, SP.Payment_Method,
               SP.Payment_Status, SP.Notes,
               (SP.Bill_Amount - SP.Amount_Paid) AS Balance_Due
        FROM SUPPLIER_PAYMENT SP
        JOIN SUPPLIER S ON SP.Supplier_ID = S.Supplier_ID
        ORDER BY SP.Payment_Date DESC, SP.Payment_ID DESC
    """, as_role='admin')

    # Supplier financial metrics
    pay_summary, _ = execute_query("""
        SELECT IFNULL(SUM(Bill_Amount), 0) AS total_billed,
               IFNULL(SUM(Amount_Paid), 0) AS total_paid,
               IFNULL(SUM(Bill_Amount - Amount_Paid), 0) AS total_pending
        FROM SUPPLIER_PAYMENT
    """, fetch_one=True, as_role='admin')

    active_tab = request.args.get('tab', 'directory')

    return render_template(
        'suppliers.html',
        suppliers=suppliers_list or [],
        payments=supplier_payments or [],
        pay_summary=pay_summary or {'total_billed': 0, 'total_paid': 0, 'total_pending': 0},
        active_tab=active_tab
    )

@app.route('/suppliers/payments/add', methods=['POST'])
def add_supplier_payment():
    try:
        supplier_id = int(request.form['supplier_id'])
        invoice_num = request.form['invoice_number'].strip()
        bill_amount = float(request.form['bill_amount'])
        amount_paid = float(request.form.get('amount_paid', 0))
        payment_date = request.form.get('payment_date', str(datetime.date.today()))
        payment_method = request.form.get('payment_method', 'Bank Transfer')
        notes = request.form.get('notes', '').strip()

        # Determine Payment Status
        if amount_paid >= bill_amount:
            payment_status = 'Paid'
        elif amount_paid > 0:
            payment_status = 'Partial'
        else:
            payment_status = 'Pending'

        # Next Payment_ID
        next_pay_res, _ = execute_query("SELECT IFNULL(MAX(Payment_ID), 500) + 1 AS next_id FROM SUPPLIER_PAYMENT", fetch_one=True, as_role='admin')
        payment_id = next_pay_res['next_id'] if next_pay_res else 501

        insert_sql = """
            INSERT INTO SUPPLIER_PAYMENT (Payment_ID, Supplier_ID, Invoice_Number, Bill_Amount, Amount_Paid, Payment_Date, Payment_Method, Payment_Status, Notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (payment_id, supplier_id, invoice_num, bill_amount, amount_paid, payment_date, payment_method, payment_status, notes)

        _, err = execute_query(insert_sql, params=params, commit=True, as_role='admin')
        if err:
            flash(f"Database error recording supplier payment: {err}", "danger")
        else:
            flash(f"Supplier invoice '{invoice_num}' and payment recorded in MySQL!", "success")

    except Exception as ex:
        flash(f"Error processing payment: {str(ex)}", "danger")

    return redirect(url_for('suppliers', tab='payments'))

@app.route('/suppliers/payments/update-status/<int:payment_id>', methods=['POST'])
def update_payment_status(payment_id):
    new_status = request.form.get('status', 'Paid')
    sql = "UPDATE SUPPLIER_PAYMENT SET Payment_Status = %s WHERE Payment_ID = %s"
    _, err = execute_query(sql, params=(new_status, payment_id), commit=True, as_role='admin')
    if err:
        flash(f"Error updating status: {err}", "danger")
    else:
        flash(f"Payment status updated to '{new_status}' in database!", "info")
    return redirect(url_for('suppliers', tab='payments'))

# -------------------------------------------------------------
# 5. STORE SETTINGS & DB CONNECTION
# -------------------------------------------------------------
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        Config.MYSQL_HOST = request.form.get('host', 'localhost')
        Config.MYSQL_PORT = int(request.form.get('port', 3306))
        Config.MYSQL_DB = request.form.get('db', 'GroceryShopDB')
        Config.MYSQL_ADMIN_USER = request.form.get('admin_user', 'root')
        Config.MYSQL_ADMIN_PASSWORD = request.form.get('admin_password', '')

        flash("Settings saved! Checking MySQL connection...", "info")
        return redirect(url_for('settings'))

    admin_status, _ = test_connection()
    return render_template('settings.html', config=Config, admin_status=admin_status)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
