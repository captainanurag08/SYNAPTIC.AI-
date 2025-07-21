from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure upload folder exists
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = 'database.db'

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                relation TEXT,
                message TEXT,
                filename TEXT,
                ip TEXT,
                device TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

init_db()

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# User login (GET shows form, POST logs in)
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['relation'] = request.form['relation']
        return redirect(url_for('user_dashboard'))
    return render_template('user_login.html')

# User dashboard – view & upload
@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'name' not in session:
        return redirect(url_for('user_login'))

    name = session['name']
    relation = session.get('relation', 'Friend')

    if request.method == 'POST':
        message = request.form['message']
        file = request.files['photo']
        filename = ''

        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

        ip = request.remote_addr
        device = request.headers.get('User-Agent')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, relation, message, filename, ip, device, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, relation, message, filename, ip, device, timestamp))
            conn.commit()

    # Show user’s own uploads
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, filename, timestamp
            FROM users
            WHERE name = ?
            ORDER BY timestamp DESC
        ''', (name,))
        rows = cursor.fetchall()

    user_entries = [
        {'message': row[0], 'filename': row[1], 'timestamp': row[2]}
        for row in rows
    ]

    return render_template('user_dashboard.html', name=name, user_entries=user_entries)

# Admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'anurag08':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

# Admin dashboard – view all uploads
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, relation, message, filename, ip, device, timestamp
            FROM users
            ORDER BY timestamp DESC
        ''')
        rows = cursor.fetchall()

    entries = [
        {
            'name': row[0],
            'relation': row[1],
            'message': row[2],
            'filename': row[3],
            'ip': row[4],
            'device': row[5],
            'timestamp': row[6]
        }
        for row in rows
    ]

    return render_template('admin_dashboard.html', entries=entries)

if __name__ == '__main__':
    app.run(debug=True)
