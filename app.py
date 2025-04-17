from flask import Flask, request, jsonify, render_template, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os
import bcrypt
import secrets


load_dotenv()


class Config:
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///cadastro.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index_login'

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

class Publicacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', backref=db.backref('publicacoes', lazy=True))


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
def index():
    return redirect('/login')

@app.route('/login')
def index_login():
    if current_user.is_authenticated:
        return redirect('/page')
    return render_template('login.html')

@app.route('/deslogar')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/cadastrar')
def index_cadastrar():
    if current_user.is_authenticated:
        return redirect('/page')
    return render_template('index.html')

@app.route('/page')
@login_required
def index_page():
    return render_template('page.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'success': False, 'error': 'Email e senha são obrigatórios'})

    user = Users.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(senha.encode('utf-8'), user.password.encode('utf-8')):
        login_user(user)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Usuário ou senha inválidos'})

@app.route('/api/cadastrar', methods=['POST'])
def cadastrar_usuario():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    senha = data.get('senha')

    if not name or not email or not senha:
        return jsonify({'success': False, 'error': 'Todos os campos são obrigatórios'})

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)

    try:
        user = Users(nome=name, email=email, password=hashed.decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Email já existe'})

@app.route('/api/publicar', methods=['POST'])
@login_required
def publicar():
    data = request.json
    conteudo = data.get('conteudo')

    if not conteudo:
        return jsonify({'success': False, 'error': 'Conteúdo não pode estar vazio'})

    publicacao = Publicacao(conteudo=conteudo, user_id=current_user.id)
    db.session.add(publicacao)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/publicacoes', methods=['GET'])
@login_required
def get_publicacoes():
    publicacoes = Publicacao.query.order_by(Publicacao.id.desc()).all()
    return jsonify([{'id': p.id, 'conteudo': p.conteudo, 'user': p.user.nome} for p in publicacoes])

@app.route('/api/deletar', methods=['POST'])
@login_required
def deletar():
    data = request.json
    publicacao_id = data.get('id')

    if not publicacao_id:
        return jsonify({'success': False, 'error': 'ID da publicação é obrigatório'})

    publicacao = Publicacao.query.get(publicacao_id)
    if publicacao and publicacao.user_id == current_user.id:
        db.session.delete(publicacao)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Você não pode deletar essa publicação'})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True)