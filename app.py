from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def setup_database():
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

setup_database()

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/login')
def index_login():
    return render_template('login.html')

@app.route('/cadastrar')
def index_cadastrar():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    senha = data['senha']
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE email = ? AND senha = ?
    ''', (email, senha))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Email ou senha incorretos'})

@app.route('/api/cadastrar', methods=['POST'])
def cadastrar_usuario():
    data = request.json
    name = data['name']
    email = data['email']
    senha = data['senha']
    try:
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (name, email, senha) VALUES (?, ?, ?)
        ''', (name, email, senha))
        conn.commit()
        conn.close()

        nome_do_arquivo = f"{name}_dados.txt"
        conteudo = f"Nome: {name}\nEmail: {email}\nSenha: {senha}\n"
        with open(nome_do_arquivo, "w") as arquivo:
            arquivo.write(conteudo)

        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Email já existe'})




if __name__ == '__main__':
    app.run(debug=True)
