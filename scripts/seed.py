import os
import sys
import secrets
import base64
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('SECRET_KEY', secrets.token_urlsafe(48))
os.environ.setdefault('CPF_AES_KEY', base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())
os.environ.setdefault('CPF_HMAC_KEY', base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())

from app import create_app, db
from app.models import Usuario, Tutor, Pet, Agendamento, Sessao, Auditoria
from app.encryption import criptografar_cpf, cpf_hmac

app = create_app()

with app.app_context():
    if db.session.query(Usuario).count() == 0:
        usuarios = [
            ('Ana Administradora', 'ana', 'Vet@2026', 'administrador'),
            ('Bruno Veterinário', 'bruno', 'Vet@2026', 'atendimento'),
            ('Carla Atendimento', 'carla', 'Vet@2026', 'atendimento'),
        ]
        for nome, login, senha, perfil in usuarios:
            usuario = Usuario(nome=nome, login=login, ativo=True, perfil=perfil)
            usuario.set_password(senha)
            db.session.add(usuario)
        db.session.commit()

    usuarios = db.session.scalars(db.select(Usuario).order_by(Usuario.id_usuario)).all()

    if db.session.query(Tutor).count() == 0:
        dados = [
            ('Mariana Souza', '52998224725', '(11) 99991-2201', 'mariana@email.com', 'Rua das Flores, 100'),
            ('Carlos Oliveira', '11144477735', '(11) 98882-3302', 'carlos@email.com', 'Av. Central, 200'),
            ('Fernanda Lima', '39053344705', '(21) 97773-4403', 'fernanda@email.com', 'Rua do Parque, 300'),
        ]
        for nome, cpf, telefone, email, endereco in dados:
            criptografado, nonce, tag = criptografar_cpf(cpf)
            db.session.add(Tutor(nome=nome, cpf_criptografado=criptografado, cpf_nonce=nonce,
                cpf_tag=tag, cpf_hmac=cpf_hmac(cpf), telefone=telefone, email=email, endereco=endereco))
        db.session.commit()

    tutores = db.session.scalars(db.select(Tutor).order_by(Tutor.id_tutor)).all()
    if db.session.query(Pet).count() == 0:
        dados = [
            ('Thor', 'Cão', 'Labrador', 'Macho', date(2022, 3, 10), 'Vacinas em dia.', tutores[0].id_tutor),
            ('Luna', 'Gato', 'Persa', 'Fêmea', date(2021, 8, 21), 'Alimentação especial.', tutores[1].id_tutor),
            ('Mel', 'Cão', 'Vira-lata', 'Fêmea', date(2023, 1, 15), 'Avaliar pele.', tutores[2].id_tutor),
        ]
        for nome, especie, raca, sexo, nascimento, observacao, id_tutor in dados:
            db.session.add(Pet(nome=nome, especie=especie, raca=raca, sexo=sexo,
                data_nascimento=nascimento, observacoes=observacao, id_tutor=id_tutor))
        db.session.commit()

    pets = db.session.scalars(db.select(Pet).order_by(Pet.id_pet)).all()
    if db.session.query(Agendamento).count() == 0:
        agora = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        for i, pet in enumerate(pets):
            db.session.add(Agendamento(data_agendamento=agora + timedelta(days=i + 1, hours=i),
                observacao=f'Revisão clínica de {pet.nome}.', status='Agendado', id_pet=pet.id_pet))
        db.session.commit()

    if db.session.query(Sessao).count() == 0:
        agora = datetime.utcnow()
        for i, usuario in enumerate(usuarios[:3]):
            inicio = agora - timedelta(hours=2 + i)
            db.session.add(Sessao(id_usuario=usuario.id_usuario,
                token_hash=secrets.token_hex(32), criado_em=inicio,
                ultima_atividade=inicio, expira_em=inicio + timedelta(minutes=20),
                encerrado_em=inicio + timedelta(minutes=5)))
        db.session.commit()

    if db.session.query(Auditoria).count() == 0:
        for i, acao in enumerate(('INICIALIZAR', 'CADASTRAR', 'CONSULTAR')):
            db.session.add(Auditoria(id_usuario=usuarios[i].id_usuario, acao=acao,
                tabela_afetada=('sistema', 'tutores', 'pets')[i], registro_id=i + 1,
                descricao='Registro de demonstração da auditoria.', data_hora=datetime.utcnow() - timedelta(minutes=i * 10)))
        db.session.commit()

    print('Banco inicializado com sucesso.')
