import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "supermarket_pos_secret"

def get_db_connection():
    conn = sqlite3.connect('supermarket.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Users Table
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)')
    # Products Table (Added GST, Unit, Purchase Price)
    conn.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, unit TEXT, 
        purchase_price REAL, price REAL, stock REAL, supplier TEXT, discount REAL, gst_percent REAL)''')
    # Sales Table
    conn.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, total_amount REAL, 
        payment_mode TEXT, date_time DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Default Credentials
    if conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin', 'Admin'))
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('yash', '123', 'Cashier'))
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def login(): return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u = request.form.get('username'); p = request.form.get('password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (u, p)).fetchone()
    conn.close()
    if user:
        session['user'], session['role'] = user['username'], user['role']
        return redirect(url_for('dashboard' if user['role'] == 'Admin' else 'billing'))
    flash("Invalid Credentials"); return redirect(url_for('login'))

# --- UPDATED: Page 2 Dashboard Logic ---
@app.route('/dashboard')
def dashboard():
    # Security: Redirect to login if user is not in session or not Admin
    if 'user' not in session or session['role'] != 'Admin':
        flash("Unauthorized access!")
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    # 1. Fetch total product count from the inventory
    product_stats = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    
    # 2. Fetch total sales sum from completed transactions
    sales_stats = conn.execute('SELECT SUM(total_amount) FROM sales').fetchone()
    total_sales = sales_stats[0] if sales_stats[0] is not None else 0.0
    
    # 3. NEW: Fetch the 5 most recent sales from the database to show in the overview table
    # 'ORDER BY id DESC LIMIT 5' ensures we get the latest entries first
    recent_transactions = conn.execute('SELECT * FROM sales ORDER BY id DESC LIMIT 5').fetchall()
    
    conn.close()

    # Pass the real database data to dashboard.html
    return render_template('dashboard.html', 
                           p_count=product_stats, 
                           s_sum=total_sales, 
                           recent_sales=recent_transactions)

@app.route('/products')
def products():
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db_connection(); db_p = conn.execute('SELECT * FROM products').fetchall(); conn.close()
    return render_template('products.html', products=db_p)

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('products'))
    f = request.form; conn = get_db_connection()
    conn.execute('''INSERT INTO products (name, category, unit, purchase_price, price, stock, supplier, discount, gst_percent) 
                 VALUES (?,?,?,?,?,?,?,?,?)''', (f.get('name'), f.get('category'), f.get('unit'), f.get('purchase_price'), 
                 f.get('price'), f.get('stock'), f.get('supplier'), f.get('discount'), f.get('gst_percent')))
    conn.commit(); conn.close(); return redirect(url_for('products'))

@app.route('/billing')
def billing():
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db_connection(); db_p = conn.execute('SELECT * FROM products').fetchall(); conn.close()
    return render_template('billing.html', products=db_p)

@app.route('/save_bill', methods=['POST'])
def save_bill():
    if 'user' not in session: return {"success": False}, 401
    data = request.get_json(); conn = get_db_connection()
    for item in data.get('items'):
        conn.execute('UPDATE products SET stock = stock - ? WHERE name = ?', (item['qty'], item['name']))
    conn.execute('INSERT INTO sales (customer_name, total_amount, payment_mode) VALUES (?, ?, ?)', 
                 (data.get('customer') or "Guest", data.get('total'), data.get('mode') or "Cash"))
    conn.commit(); conn.close(); return {"success": True}

@app.route('/history')
def history():
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('login'))
    conn = get_db_connection(); sales = conn.execute('SELECT * FROM sales ORDER BY id DESC').fetchall()
    total = sum(s['total_amount'] for s in sales); conn.close()
    return render_template('history.html', sales=sales, total=total, count=len(sales))

@app.route('/reports')
def reports():
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('login'))
    conn = get_db_connection()
    cost = conn.execute('SELECT SUM(purchase_price * stock) FROM products').fetchone()[0] or 0
    val = conn.execute('SELECT SUM(price * stock) FROM products').fetchone()[0] or 0
    low = conn.execute('SELECT name, stock, unit FROM products WHERE stock < 10').fetchall(); conn.close()
    return render_template('reports.html', investment=cost, revenue=val, profit=val-cost, low_stock=low)

@app.route('/suppliers')
def suppliers():
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('login'))
    conn = get_db_connection(); summary = conn.execute('SELECT supplier, COUNT(*) as item_count FROM products GROUP BY supplier').fetchall(); conn.close()
    return render_template('suppliers.html', suppliers=summary)

@app.route('/supplier_products/<name>')
def supplier_products(name):
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('login'))
    conn = get_db_connection(); p = conn.execute('SELECT * FROM products WHERE supplier = ?', (name,)).fetchall(); conn.close()
    return render_template('supplier_products.html', products=p, supplier_name=name)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('products'))
    conn = get_db_connection(); conn.execute('DELETE FROM products WHERE id = ?', (id,)); conn.commit(); conn.close()
    return redirect(url_for('products'))

@app.route('/delete_sale/<int:id>')
def delete_sale(id):
    if 'user' not in session or session['role'] != 'Admin': return redirect(url_for('login'))
    conn = get_db_connection(); conn.execute('DELETE FROM sales WHERE id = ?', (id,)); conn.commit(); conn.close()
    return redirect(url_for('history'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == '__main__': app.run(debug=True)