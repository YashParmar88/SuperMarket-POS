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

# Updated Database Initialization with Supplier and Discount support
def init_db():
    conn = get_db_connection()
    
    # 1. Users Table (No changes)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )''')

    # 2. Products table with NEW columns: purchase_price, supplier, discount
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, 
            category TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'Pcs',
            purchase_price REAL NOT NULL DEFAULT 0, -- NEW: Price at which store buys
            price REAL NOT NULL,                    -- Selling Price
            stock REAL NOT NULL,
            supplier TEXT,                         -- NEW: Supplier name
            discount REAL DEFAULT 0                -- NEW: Default discount %
        )''')

    # 3. Sales table (No changes)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_amount REAL,
            payment_mode TEXT,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

    # Insert default users
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
        session['user'] = user['username']; session['role'] = user['role'] 
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

# Updated add_product to handle supplier, purchase price and discount
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session or session['role'] != 'Admin': 
        flash("Unauthorized action."); return redirect(url_for('products'))
    
    name = request.form.get('name')
    cat = request.form.get('category')
    unit = request.form.get('unit')
    p_price = request.form.get('purchase_price') # New
    s_price = request.form.get('price')          # Selling price
    stock = request.form.get('stock')
    supp = request.form.get('supplier')          # New
    disc = request.form.get('discount')          # New
    
    conn = get_db_connection()
    conn.execute('''INSERT INTO products 
                 (name, category, unit, purchase_price, price, stock, supplier, discount) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                 (name, cat, unit, p_price, s_price, stock, supp, disc))
    conn.commit(); conn.close()
    flash("Product added successfully with details.")
    return redirect(url_for('products'))

@app.route('/billing')
def billing():
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('billing.html', products=db_products)

@app.route('/save_bill', methods=['POST'])
def save_bill():
    if 'user' not in session: return {"success": False}, 401
    data = request.get_json()
    customer = data.get('customer') or "Guest"
    mode = data.get('mode') or "Cash"
    conn = get_db_connection()
    for item in data.get('items'):
        conn.execute('UPDATE products SET stock = stock - ? WHERE name = ?', (item['qty'], item['name']))
    conn.execute('INSERT INTO sales (customer_name, total_amount, payment_mode) VALUES (?, ?, ?)',
                 (customer, data.get('total'), mode))
    conn.commit(); conn.close()
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