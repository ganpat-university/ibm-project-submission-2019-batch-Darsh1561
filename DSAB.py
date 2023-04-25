import hashlib
import datetime as date
import os
from flask import Flask, jsonify, request, render_template
from flask import Flask, request, render_template, redirect, url_for, session, flash
import hashlib
import sqlite3
import re
import datetime
import hashlib
import simplejson as json
from flask import Flask, jsonify
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from cryptography.fernet import Fernet
from flask import Flask, send_file

class Block:
    def __init__(self, index, timestamp, file_name, file_hash, previous_hash, uploaded_by=None):
        self.index = index
        self.timestamp = timestamp
        self.file_name = file_name
        self.file_hash = file_hash
        self.previous_hash = previous_hash
        self.uploaded_by = uploaded_by
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_contents = str(self.index) + str(self.timestamp) + self.file_name + self.file_hash + self.previous_hash + str(self.uploaded_by)
        block_hash = hashlib.sha256(block_contents.encode()).hexdigest()
        return block_hash

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, date.datetime.now(), "Genesis Block", "0", "None")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, file_name, file_content, uploaded_by):
        index = len(self.chain)
        timestamp = date.datetime.now()
        data = hashlib.sha256(file_content).hexdigest()
        previous_hash = self.get_latest_block().hash
        new_block = Block(index, timestamp, file_name, data, previous_hash, uploaded_by)
        self.chain.append(new_block)

def hash_password(password):
    password = password.encode('utf-8')
    hashed_password = hashlib.sha256(password).hexdigest()
    return hashed_password

def validate_password(password):
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    if not re.search("[a-z]", password):
        return 'Password must have at least one lowercase letter.'
    if not re.search("[A-Z]", password):
        return 'Password must have at least one uppercase letter.'
    if not re.search("[0-9]", password):
        return 'Password must have at least one number.'
    special_chars = '[@$!%*#?&]'
    if not re.search(special_chars, password):
        return f'Password must have at least one special character ({special_chars}).'
    if len(re.findall(special_chars, password)) < 2:
        return f'Password must have at least two special characters ({special_chars}).'
    return True


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'files'
ALLOWED_EXTENSIONS = {'pdf'}

blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

# Handle file upload
@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if 'file' not in request.files:
        message = 'No file selected'
        return render_template('fileupload.html', message=message)
    
    file = request.files['file']
    if file:
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))  # Save the file locally
        filename = file.filename
        if filename.split('.')[-1].lower() == 'pdf':
            uploaded_by = session['username']
            file_content = file.read()
            blockchain.add_block(filename, file_content, uploaded_by)
            file_hash = hashlib.sha256(file_content).hexdigest()
            message = 'File uploaded successfully'
            return render_template('fileupload.html', message=message, file_hash=file_hash)
        else:
            message = 'Please upload a PDF file'
    else:
        message = 'No file selected'
    return render_template('fileupload.html', message=message)



@app.route('/blockchain')
def blockchain_display():
    return render_template('blockchain.html', blockchain=blockchain.chain)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not validate_password(password):
            flash('Password must be at least 8 characters long and contain at least one uppercase letter and one number.')
            return render_template('register.html')
        hashed_password = hash_password(password)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('upload_file'))
        else:
            error = 'Invalid login. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/download/<filename>')
def download_file(filename):
    file = ""
    file = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'])
    path = file + "//" + filename
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    conn.close()
    app.run(debug=True)
