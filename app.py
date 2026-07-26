import sqlite3

# Function to connect to the SQLite database
def get_db_connection():
    # This creates a connection to supermarket.db file
    conn = sqlite3.connect('supermarket.db')
    conn.row_factory = sqlite3.Row # This helps to access columns by name
    return conn

# Create the products table if it doesn't exist
def init_db():
    conn = get_db_connection()
    # Creating a table for products with necessary columns
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the script starts
init_db()








from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
# Secret key is required for sessions and flash messages security
app.secret_key = "supermarket_secret_key"

# Page 1: Login Route
@app.route('/')
def login():
    return render_template('login.html')

# Logic for processing the login form
@app.route('/login_process', methods=['POST'])
def login_process():
    # Getting data from the HTML form fields
    user = request.form.get('username')
    pwd = request.form.get('password')

    # Checking credentials
    if user == "admin" and pwd == "123":
        # Create a session to remember that user is logged in
        session['user'] = user 
        return redirect(url_for('dashboard'))
    else:
        # If credentials are wrong, show error and stay on login page
        flash("Invalid Username or Password. Please try again.")
        return redirect(url_for('login'))

# Page 2: Dashboard Route (Protected)
@app.route('/dashboard')
def dashboard():
    # Security: Redirect to login if user is not in session
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Page 3: Products Management Route (Protected)
# Updated Page 3: Products Management Route with Database
@app.route('/products')
def products():
    # Security check
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Fetch all items from the database to display in the table
    conn = get_db_connection()
    db_products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    return render_template('products.html', products=db_products)

# New Route to handle adding a product (POST method)
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Collect data from the HTML form fields
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    stock = request.form.get('stock')

    # Save the new product into the database
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)',
                 (name, category, price, stock))
    conn.commit()
    conn.close()

    # Redirect back to the products page to see the new entry
    return redirect(url_for('products'))

# Page 4: Billing Counter Route (Protected)
@app.route('/billing')
def billing():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('billing.html')

# Page 5: Sales History Route (Protected)
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('history.html')

# Route to clear session and logout user
@app.route('/logout')
def logout():
    # Remove user data from session
    session.pop('user', None) 
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))






if __name__ == '__main__':
    app.run(debug=True)