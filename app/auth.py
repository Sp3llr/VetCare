from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from . import db
from .models import Usuario, BloqueioLogin
from .forms import LoginForm, CadastroForm
from .session_manager import iniciar_sessao, encerrar_sessao


auth_bp = Blueprint('auth', __name__)
login_tentativas = {}


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = CadastroForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        login = form.login.data.strip().lower()
        usuario_existente = db.session.scalar(db.select(Usuario).where(Usuario.login == login))
        if usuario_existente:
            flash('Este nome de usuário já está em uso.', 'danger')
            return render_template('cadastro.html', form=form)

        usuario = Usuario(nome=nome, login=login, ativo=True, perfil='atendimento')
        usuario.set_password(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso. Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('cadastro.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data.strip()
        agora = datetime.utcnow()
        ip = request.remote_addr or 'desconhecido'
        chave = f'{login.lower()}|{ip}'
        bloqueio = db.session.scalar(db.select(BloqueioLogin).where(BloqueioLogin.chave == chave))
        if bloqueio and bloqueio.bloqueado_ate and bloqueio.bloqueado_ate > agora:
            flash('Login bloqueado temporariamente devido a tentativas excessivas.', 'danger')
            return render_template('login.html', form=form)
        usuario = db.session.scalar(db.select(Usuario).where(Usuario.login == login, Usuario.ativo.is_(True)))
        if usuario and usuario.check_password(form.senha.data):
            if bloqueio:
                db.session.delete(bloqueio)
                db.session.commit()
            login_user(usuario)
            iniciar_sessao(usuario)
            return redirect(url_for('main.dashboard'))
        if not bloqueio:
            bloqueio = BloqueioLogin(chave=chave)
            db.session.add(bloqueio)
        bloqueio.falhas = (bloqueio.falhas or 0) + 1
        if bloqueio.falhas >= 5:
            bloqueio.bloqueado_ate = agora + timedelta(minutes=15)
        db.session.commit()
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    usuario_id = current_user.id_usuario if current_user.is_authenticated else None
    encerrar_sessao(usuario_id)
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth.login'))
