import os
import secrets
import base64
import pytest

os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('CPF_AES_KEY', base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())
os.environ.setdefault('CPF_HMAC_KEY', base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())

from app import create_app, db
from app.models import Usuario, Tutor, Pet, Agendamento, Sessao, BloqueioLogin
from app.encryption import criptografar_cpf, cpf_hmac
from datetime import datetime, timedelta, date


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret'
    CPF_AES_KEY = os.environ['CPF_AES_KEY']
    CPF_HMAC_KEY = os.environ['CPF_HMAC_KEY']
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        usuario = Usuario(nome='Teste', login='teste', ativo=True)
        usuario.set_password('Senha@123')
        db.session.add(usuario)
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client):
    return client.post('/login', data={'login': 'teste', 'senha': 'Senha@123'})


def test_login_correto_e_bloqueio_sem_autenticacao(client):
    assert login(client).status_code == 302
    novo = client.application.test_client()
    resposta = novo.get('/tutores')
    assert resposta.status_code == 302


def test_login_incorreto(client):
    resposta = client.post('/login', data={'login': 'teste', 'senha': 'errada'})
    assert resposta.status_code == 200
    assert b'inv' in resposta.data.lower()


def test_cpf_criptografado_e_pesquisa(app, client):
    login(client)
    from app.encryption import criptografar_cpf, cpf_hmac
    with app.app_context():
        criptografado, nonce, tag = criptografar_cpf('52998224725')
        tutor = Tutor(nome='Teste CPF', cpf_criptografado=criptografado,
            cpf_nonce=nonce, cpf_tag=tag, cpf_hmac=cpf_hmac('52998224725'),
            telefone='11999990000')
        db.session.add(tutor)
        db.session.commit()
        assert '52998224725' not in tutor.cpf_criptografado
        assert tutor.cpf_hmac


def test_sessao_persistida_e_logout(app, client):
    login(client)
    with app.app_context():
        assert db.session.query(Sessao).count() == 1
    resposta = client.post('/logout')
    assert resposta.status_code == 302
    with app.app_context():
        sessao = db.session.scalar(db.select(Sessao))
        assert sessao.encerrado_em is not None


def test_bloqueio_login_persistente(app, client):
    for _ in range(5):
        client.post('/login', data={'login': 'teste', 'senha': 'errada'})
    with app.app_context():
        bloqueio = db.session.scalar(db.select(BloqueioLogin))
        assert bloqueio is not None
        assert bloqueio.falhas >= 5


def test_cadastro_cria_usuario_atendimento(app, client):
    resposta = client.post('/cadastro', data={
        'nome': 'Maria Atendimento',
        'login': 'maria.atendimento',
        'senha': 'SenhaSegura123',
        'confirmar_senha': 'SenhaSegura123',
    })
    assert resposta.status_code == 302
    with app.app_context():
        usuario = db.session.scalar(db.select(Usuario).where(Usuario.login == 'maria.atendimento'))
        assert usuario is not None
        assert usuario.perfil == 'atendimento'
        assert usuario.check_password('SenhaSegura123')


def test_cadastro_rejeita_senha_fraca(client):
    resposta = client.post('/cadastro', data={
        'nome': 'Usuario Senha Fraca',
        'login': 'senha.fraca',
        'senha': '12345678',
        'confirmar_senha': '12345678',
    })
    assert resposta.status_code == 200


def test_cadastro_rejeita_login_duplicado(app, client):
    primeira = client.post('/cadastro', data={
        'nome': 'Primeiro Usuario', 'login': 'usuario.unico',
        'senha': 'SenhaSegura123', 'confirmar_senha': 'SenhaSegura123',
    })
    segunda = client.post('/cadastro', data={
        'nome': 'Segundo Usuario', 'login': 'usuario.unico',
        'senha': 'OutraSenha123', 'confirmar_senha': 'OutraSenha123',
    })
    assert primeira.status_code == 302
    assert segunda.status_code == 200
    assert b'j\xc3\xa1 est\xc3\xa1 em uso' in segunda.data


def test_auditoria_bloqueada_para_atendimento(app, client):
    with app.app_context():
        usuario = Usuario(nome='Atendimento', login='atendimento_teste', ativo=True, perfil='atendimento')
        usuario.set_password('Senha@123')
        db.session.add(usuario)
        db.session.commit()
    client.post('/login', data={'login': 'atendimento_teste', 'senha': 'Senha@123'})
    resposta = client.get('/auditoria')
    assert resposta.status_code == 302


def test_agendamentos_bloqueiam_passado_e_conflito(app, client):
    login(client)
    with app.app_context():
        criptografado, nonce, tag = criptografar_cpf('52998224725')
        tutor = Tutor(nome='Tutor Teste', cpf_criptografado=criptografado,
            cpf_nonce=nonce, cpf_tag=tag, cpf_hmac=cpf_hmac('52998224725'),
            telefone='11999990000')
        db.session.add(tutor)
        db.session.flush()
        pet = Pet(nome='Rex', especie='Cão', raca='SRD', sexo='Macho',
            data_nascimento=date(2022, 1, 1), id_tutor=tutor.id_tutor)
        db.session.add(pet)
        db.session.flush()
        futuro = datetime.utcnow() + timedelta(days=2)
        agendamento = Agendamento(data_agendamento=futuro, status='Agendado', id_pet=pet.id_pet)
        db.session.add(agendamento)
        db.session.commit()
        pet_id = pet.id_pet

    resposta = client.post('/agendamentos', data={
        'id_pet': str(pet_id),
        'data_agendamento': (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'observacao': 'Teste passado',
        'status': 'Agendado',
    })
    assert resposta.status_code == 302

    resposta = client.post('/agendamentos', data={
        'id_pet': str(pet_id),
        'data_agendamento': futuro.strftime('%Y-%m-%dT%H:%M'),
        'observacao': 'Teste conflito',
        'status': 'Agendado',
    })
    assert resposta.status_code == 302
