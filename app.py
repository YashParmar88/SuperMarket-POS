import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
# Secret key is required for sessions and flash messages security
app.secret_key = "supermarket_secret_key"

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('supermarket.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the products and sales tables if they don't exist
def init_db():
    conn = get_db_connection()
    # 1. Table to store product information
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, 
            category TEXT NOT NULL,
            price REAL NOT NULL, 
            stock INTEGER NOT NULL
        )
    ''')
    # 2. Table to store completed sales/transactions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_amount REAL,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the server starts
init_db()

# Page 1: Login Route
@app.route('/')
def login():
    return render_template('login.html')

# Logic for processing the login form
@app.route('/login_process', methods=['POST'])
def login_process():
    user = request.form.get('username')
    pwd = request.form.get('password')

    if user == "admin" and pwd == "123":
        session['user'] = user 
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid Username or Password. Please try again.")
        return redirect(url_for('login'))

# Page 2: Dashboard Route (Protected)
# Updated Page 2: Dashboard Route to show real-time statistics
@app.route('/dashboard')
def dashboard():
    # Security: Redirect to login if user is not in session
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    # 1. Fetch total count of products in the inventory
    product_stats = conn.execute('SELECT COUNT(*) FROM products').fetchone()
    total_products = product_stats[0] if product_stats else 0
    
    # 2. Fetch total sum of all sales generated so far
    sales_stats = conn.execute('SELECT SUM(total_amount) FROM sales').fetchone()
    total_sales = sales_stats[0] if sales_stats[0] is not None else 0.0
    
    conn.close()

    # Pass the calculated stats to the dashboard template
    return render_template('dashboard.html', p_count=total_products, s_sum=total_sales)

# Page 3: Products Management Route (Protected)
@app.route('/products')
def products():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('products.html', products=db_products)

# Logic to add a new product
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    stock = request.form.get('stock')
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)',
                 (name, category, price, stock))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

# Page 4: Billing Counter Route (Protected)
@app.route('/billing')
def billing():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('billing.html', products=db_products)

# Logic to save the bill
@app.route('/save_bill', methods=['POST'])
def save_bill():
    if 'user' not in session:
        return {"success": False, "message": "Unauthorized"}, 401
    
    # Getting JSON data from JavaScript
    data = request.get_json()
    grand_total = data.get('total')
    items_sold = data.get('items') # This is the list of products in the cart

    if not items_sold:
        return {"success": False, "message": "Cart is empty"}, 400
    
    conn = get_db_connection()
    
    # Loop through each item in the cart to update the stock
    for item in items_sold:
        # SQL logic: Subtract the sold quantity from current inventory stock
        conn.execute('UPDATE products SET stock = stock - ? WHERE name = ?',
                     (item['qty'], item['name']))
    
    # Save the transaction record
    conn.execute('INSERT INTO sales (customer_name, total_amount) VALUES (?, ?)',
                 ("Guest Customer", grand_total))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Bill generated and Stock updated successfully!"}

# Page 5: Sales History Route (Protected)
# Updated Page 5: Sales History Route to fetch real transactions
@app.route('/history')
def history():
    # Security check: Ensure admin is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    # Fetch all records from 'sales' table, sorted by latest first
    all_sales = conn.execute('SELECT * FROM sales ORDER BY id DESC').fetchall()
    
    # Simple calculation for summary cards
    total_revenue = 0
    for sale in all_sales:
        total_revenue += sale['total_amount']
    
    bill_count = len(all_sales)
    conn.close()
    
    # Passing data and counts to the HTML template
    return render_template('history.html', sales=all_sales, total=total_revenue, count=bill_count)






if __name__ == '__main__':
    app.run(debug=True)