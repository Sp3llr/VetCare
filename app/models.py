from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Index
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    login = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    perfil = db.Column(db.String(30), nullable=False, default='atendimento')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_id(self):
        return str(self.id_usuario)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


class Tutor(db.Model):
    __tablename__ = 'tutores'
    id_tutor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf_criptografado = db.Column(db.Text, nullable=False)
    cpf_nonce = db.Column(db.String(64), nullable=False)
    cpf_tag = db.Column(db.String(64), nullable=False)
    cpf_hmac = db.Column(db.String(64), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    endereco = db.Column(db.String(255), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    pets = db.relationship('Pet', back_populates='tutor', cascade='all, delete-orphan')


class Pet(db.Model):
    __tablename__ = 'pets'
    id_pet = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(100), nullable=False)
    sexo = db.Column(db.String(20), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    id_tutor = db.Column(db.Integer, db.ForeignKey('tutores.id_tutor'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tutor = db.relationship('Tutor', back_populates='pets')
    agendamentos = db.relationship('Agendamento', back_populates='pet', cascade='all, delete-orphan')


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    id_agendamento = db.Column(db.Integer, primary_key=True)
    data_agendamento = db.Column(db.DateTime, nullable=False)
    observacao = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=False, default='Agendado')
    id_pet = db.Column(db.Integer, db.ForeignKey('pets.id_pet'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    pet = db.relationship('Pet', back_populates='agendamentos')


class Sessao(db.Model):
    __tablename__ = 'sessoes'
    id_sessao = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultima_atividade = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expira_em = db.Column(db.DateTime, nullable=False)
    encerrado_em = db.Column(db.DateTime, nullable=True)


class BloqueioLogin(db.Model):
    __tablename__ = 'bloqueios_login'
    id_bloqueio = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(255), unique=True, nullable=False)
    falhas = db.Column(db.Integer, nullable=False, default=0)
    bloqueado_ate = db.Column(db.DateTime, nullable=True)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    id_auditoria = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    acao = db.Column(db.String(100), nullable=False)
    tabela_afetada = db.Column(db.String(100), nullable=False)
    registro_id = db.Column(db.Integer, nullable=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    descricao = db.Column(db.Text, nullable=False)


Index('ix_tutores_nome', Tutor.nome)
Index('ix_agendamentos_data', Agendamento.data_agendamento)
