from flask import Flask, render_template, request, redirect, url_for, session
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # You can change this
UPLOAD_FOLDER = 'static/uploads'
MESSAGE_FILE = 'messages.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, 'r') as f:
            messages = json.load(f)
    else:
        messages = {}
    return render_template('index.html', files=files, messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pw = request.form.get('password')
        if pw == '4234':  # ✅ Change this to your shared password
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return "❌ Incorrect password"
    return """
    <form method='POST'>
        <h2>Enter Shared Password</h2>
        <input type='password' name='password' placeholder='Password'>
        <button type='submit'>Enter</button>
    </form>
    """

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return redirect(url_for('home'))

    photo = request.files['photo']
    name = request.form.get('name', 'Anonymous')
    message = request.form.get('message', '')

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)

        if os.path.exists(MESSAGE_FILE):
            with open(MESSAGE_FILE, 'r') as f:
                messages = json.load(f)
        else:
            messages = {}

        messages[filename] = {
            'name': name,
            'message': message
        }

        with open(MESSAGE_FILE, 'w') as f:
            json.dump(messages, f)

    return redirect(url_for('home'))


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
