import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
# Secret key for session security
app.secret_key = "supermarket_secret_key"

# Database Connection Function
def get_db_connection():
    conn = sqlite3.connect('supermarket.db')
    conn.row_factory = sqlite3.Row
    return conn

# Updated Database Initialization
def init_db():
    conn = get_db_connection()
    
    # 1. Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # 2. Products table (Stock supports decimal for weights)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, 
            category TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'Pcs',
            price REAL NOT NULL, 
            stock REAL NOT NULL 
        )
    ''')

    # 3. Updated Sales table with payment_mode column
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_amount REAL,
            payment_mode TEXT, -- NEW: To store Cash/Card/Online info
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default users for testing
    user_check = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_check == 0:
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin', 'Admin'))
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('yash', '123', 'Cashier'))

    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    if user:
        session['user'] = user['username']
        session['role'] = user['role'] 
        return redirect(url_for('dashboard')) if user['role'] == 'Admin' else redirect(url_for('billing'))
    flash("Invalid Credentials."); return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('login'))
    conn = get_db_connection()
    p_count = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    sales_stats = conn.execute('SELECT SUM(total_amount) FROM sales').fetchone()
    conn.close()
    s_total = sales_stats[0] if sales_stats[0] is not None else 0.0
    return render_template('dashboard.html', p_count=p_count, s_sum=s_total)

@app.route('/products')
def products():
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('products.html', products=db_products)

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('products'))
    name = request.form.get('name'); cat = request.form.get('category')
    unit = request.form.get('unit'); price = request.form.get('price'); stock = request.form.get('stock')
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, category, unit, price, stock) VALUES (?, ?, ?, ?, ?)', (name, cat, unit, price, stock))
    conn.commit(); conn.close()
    return redirect(url_for('products'))

@app.route('/billing')
def billing():
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('billing.html', products=db_products)

# Updated save_bill route to handle Customer Name and Payment Mode
@app.route('/save_bill', methods=['POST'])
def save_bill():
    if 'user' not in session: return {"success": False}, 401
    
    data = request.get_json()
    total_val = data.get('total')
    items_list = data.get('items')
    
    # 1. Logic for Optional Customer Name
    customer = data.get('customer')
    if not customer or customer.strip() == "":
        customer = "Guest" # Fallback to Guest if name is empty
    
    # 2. Logic for Payment Mode
    mode = data.get('mode') or "Cash"

    conn = get_db_connection()
    # Update Stock
    for item in items_list:
        conn.execute('UPDATE products SET stock = stock - ? WHERE name = ?', (item['qty'], item['name']))
    
    # 3. Save to Sales table with new columns
    conn.execute('INSERT INTO sales (customer_name, total_amount, payment_mode) VALUES (?, ?, ?)',
                 (customer, total_val, mode))
    
    conn.commit()
    conn.close()
    return {"success": True, "message": "Bill generated successfully!"}

@app.route('/history')
def history():
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('login'))
    conn = get_db_connection()
    all_sales = conn.execute('SELECT * FROM sales ORDER BY id DESC').fetchall()
    total_rev = sum(sale['total_amount'] for sale in all_sales)
    conn.close()
    return render_template('history.html', sales=all_sales, total=total_rev, count=len(all_sales))

@app.route('/delete_product/<int:id>')
def delete_product(id):
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('products'))
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit(); conn.close()
    return redirect(url_for('products'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)