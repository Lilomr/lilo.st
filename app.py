from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cadastro.db"
app.config["SECRET_KEY"] = "ENTER YOUR SECRET KEY"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)
class Users( db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True,
                        nullable=False)
    password = db.Column(db.String(250),
                        nullable=False)

db.app = app(app)
with app.app_context():
    db.create_all()
    
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/login')
def index_login():
    return render_template('login.html')

@app.route('/cadastrar')
def index_cadastrar():
    return render_template('index.html')

@app.route('/page')
def index_page():
    return render_template('page.html')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    senha = data['senha']
    user = Users.query.filter_by(email=email, password=senha).first()
    if user:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'A conta não existe'})

@app.route('/api/cadastrar', methods=['POST'])
def cadastrar_usuario():
    data = request.json
    name = data['name']
    email = data['email']
    senha = data['senha']
    try:
        user = Users(nome=name, email=email, password=senha)
        db.session.add(user)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Email já existe'})


if __name__ == '__main__':
    app.run(debug=True)
