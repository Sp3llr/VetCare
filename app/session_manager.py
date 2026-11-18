import hashlib
import secrets
from datetime import datetime, timedelta
from flask import session
from .models import Sessao, db


def iniciar_sessao(usuario):
    token = secrets.token_urlsafe(48)
    agora = datetime.utcnow()
    registro = Sessao(
        id_usuario=usuario.id_usuario,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        criado_em=agora,
        ultima_atividade=agora,
        expira_em=agora + timedelta(hours=8),
    )
    db.session.add(registro)
    db.session.commit()
    for key in ('session_token_hash', 'session_id', 'inicio_sessao', 'ultima_atividade'):
        session.pop(key, None)
    session.permanent = True
    session['session_token_hash'] = hashlib.sha256(token.encode()).hexdigest()
    session['session_id'] = registro.id_sessao
    session['inicio_sessao'] = agora.isoformat()
    session['ultima_atividade'] = agora.isoformat()


def encerrar_sessao(usuario_id=None):
    sessao_id = session.pop('session_id', None)
    if usuario_id:
        registros = db.session.scalars(
            db.select(Sessao).where(Sessao.id_usuario == usuario_id, Sessao.encerrado_em.is_(None))
        ).all()
    elif sessao_id:
        registro = db.session.get(Sessao, sessao_id)
        registros = [registro] if registro else []
    else:
        registros = []

    agora = datetime.utcnow()
    for registro in registros:
        registro.encerrado_em = agora
    db.session.commit()
