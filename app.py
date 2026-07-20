from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Page 1: Login Route
@app.route('/')
def login():
    return render_template('login.html')

# Login process logic
@app.route('/login_process', methods=['POST'])
def login_process():
    return redirect(url_for('login'))

   # Dashboard ka rasta (Route)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)

 