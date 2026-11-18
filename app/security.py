from datetime import datetime, timedelta
from flask import session, redirect, url_for, flash, request
from flask_login import current_user, logout_user
from .models import Usuario, Auditoria, Sessao, db

INATIVIDADE_MINUTOS = 20
SESSAO_ABSOLUTA_HORAS = 8


def registrar_auditoria(acao, tabela, registro_id=None, descricao=''):
    usuario_id = current_user.id_usuario if current_user.is_authenticated else None
    db.session.add(Auditoria(
        id_usuario=usuario_id,
        acao=acao,
        tabela_afetada=tabela,
        registro_id=registro_id,
        descricao=descricao,
    ))


def validar_sessao_servidor():
    if request.endpoint in ('auth.login', 'auth.cadastro', 'auth.realizar_login', 'static'):
        return None
    if not current_user.is_authenticated:
        return None
    agora = datetime.utcnow()
    sessao_id = session.get('session_id')
    token_hash = session.get('session_token_hash')
    registro = db.session.get(Sessao, sessao_id) if sessao_id else None

    expirou = not registro or registro.encerrado_em is not None
    if registro:
        expirou = expirou or registro.id_usuario != current_user.id_usuario
        expirou = expirou or registro.token_hash != token_hash
        expirou = expirou or agora - registro.ultima_atividade > timedelta(minutes=INATIVIDADE_MINUTOS)
        expirou = expirou or agora - registro.criado_em > timedelta(hours=SESSAO_ABSOLUTA_HORAS)
        expirou = expirou or registro.expira_em <= agora
    if expirou:
        logout_user()
        session.clear()
        flash('Sua sessão expirou por inatividade ou tempo máximo.', 'warning')
        return redirect(url_for('auth.login'))
    registro.ultima_atividade = agora
    db.session.commit()
    session['ultima_atividade'] = agora.isoformat()
    session.permanent = True
    return None
