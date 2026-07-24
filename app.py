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
@app.route('/products')
def products():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('products.html')

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