import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
# Secret key for session security and flash messages
app.secret_key = "supermarket_secret_key"

# Database Connection Function
def get_db_connection():
    conn = sqlite3.connect('supermarket.db')
    conn.row_factory = sqlite3.Row
    return conn

# Updated Database Initialization with Users table for Roles
def init_db():
    conn = get_db_connection()
    
    # 1. Create Users Table (Admin vs Cashier)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL -- Value will be 'Admin' or 'Cashier'
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

    # 3. Sales history table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_amount REAL,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default users for testing (Only if table is empty)
    user_check = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_check == 0:
        # Admin User: admin / admin
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                     ('admin', 'admin', 'Admin'))
        # Cashier User: yash / 123
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                     ('yash', '123', 'Cashier'))

    conn.commit()
    conn.close()

# Initialize database
init_db()

# Page 1: Login Route
@app.route('/')
def login():
    return render_template('login.html')

# Logic for processing login based on database roles
@app.route('/login_process', methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    # Check if user exists in the database
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                        (username, password)).fetchone()
    conn.close()

    if user:
        # Store user info and role in the session
        session['user'] = user['username']
        session['role'] = user['role'] 
        
        # Redirection logic based on role
        if user['role'] == 'Admin':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('billing'))
    else:
        flash("Invalid Username or Password. Access Denied.")
        return redirect(url_for('login'))

# Page 2: Dashboard (Admin Only)
@app.route('/dashboard')
def dashboard():
    # Security: If not Admin, kick back to login or billing
    if 'user' not in session or session['role'] != 'Admin':
        flash("Unauthorized access! Admins only.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    product_stats = conn.execute('SELECT COUNT(*) FROM products').fetchone()
    sales_stats = conn.execute('SELECT SUM(total_amount) FROM sales').fetchone()
    conn.close()
    s_total = sales_stats[0] if sales_stats[0] is not None else 0.0
    return render_template('dashboard.html', p_count=product_stats[0], s_sum=s_total)

# Page 3: Products Management (All logged users can view)
@app.route('/products')
def products():
    if 'user' not in session: 
        return redirect(url_for('login'))
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('products.html', products=db_products)

# Logic to add a product (Admin Only)
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session or session['role'] != 'Admin': 
        flash("You do not have permission to add stock.")
        return redirect(url_for('products'))

    name = request.form.get('name')
    category = request.form.get('category')
    unit = request.form.get('unit')
    price = request.form.get('price')
    stock = request.form.get('stock')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, category, unit, price, stock) VALUES (?, ?, ?, ?, ?)',
                 (name, category, unit, price, stock))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

# Page 4: Billing Counter (Both Admin & Cashier can access)
@app.route('/billing')
def billing():
    if 'user' not in session: 
        return redirect(url_for('login'))
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('billing.html', products=db_products)

@app.route('/save_bill', methods=['POST'])
def save_bill():
    if 'user' not in session: return {"success": False}, 401
    data = request.get_json()
    conn = get_db_connection()
    for item in data.get('items'):
        conn.execute('UPDATE products SET stock = stock - ? WHERE name = ?',
                     (item['qty'], item['name']))
    conn.execute('INSERT INTO sales (customer_name, total_amount) VALUES (?, ?)',
                 ("Guest Customer", data.get('total')))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Transaction complete!"}

# Page 5: Sales History (Admin Only)
@app.route('/history')
def history():
    if 'user' not in session or session['role'] != 'Admin': 
        flash("History access restricted to Admins.")
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    all_sales = conn.execute('SELECT * FROM sales ORDER BY id DESC').fetchall()
    total_rev = sum(sale['total_amount'] for sale in all_sales)
    conn.close()
    return render_template('history.html', sales=all_sales, total=total_rev, count=len(all_sales))

# Delete Product (Admin Only)
@app.route('/delete_product/<int:id>')
def delete_product(id):
    if 'user' not in session or session['role'] != 'Admin': 
        flash("Permission denied.")
        return redirect(url_for('products'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

@app.route('/logout')
def logout():
    session.clear() # Clears all session data (User + Role)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)