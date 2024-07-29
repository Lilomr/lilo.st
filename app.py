from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required



app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key' 

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cadastro.db"
app.config["SECRET_KEY"] = "ENTER YOUR SECRET KEY"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True,
                        nullable=False)
    password = db.Column(db.String(250),
                        nullable=False)

db.init_app(app)
with app.app_context():
    db.app = app
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

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
@login_required
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
        login_user(user)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Usuário não encontrado'})
    
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
    except sqlite3.IntegrityError as e:
        print(e)
        return jsonify({'success': False, 'error': 'email já existe'})


if __name__ == '__main__':
    app.run(debug=True)
