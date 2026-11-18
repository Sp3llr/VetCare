from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from . import db
from .models import Tutor, Pet, Agendamento, Usuario, Sessao, Auditoria
from .forms import TutorForm, PetForm, AgendamentoForm
from .encryption import validar_cpf, criptografar_cpf, cpf_hmac, mascarar_cpf, descriptografar_cpf
from .security import registrar_auditoria, validar_sessao_servidor

main_bp = Blueprint('main', __name__)


@main_bp.before_app_request
def verificar_sessao():
    return validar_sessao_servidor()


@main_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html',
        tutores=db.session.scalar(db.select(db.func.count()).select_from(Tutor)) or 0,
        pets=db.session.scalar(db.select(db.func.count()).select_from(Pet)) or 0,
        agendamentos=db.session.scalar(db.select(db.func.count()).select_from(Agendamento)) or 0,
        recentes=db.session.scalars(db.select(Agendamento).where(Agendamento.status != 'Cancelado').order_by(Agendamento.data_agendamento.asc()).limit(5)).all(),
    )


@main_bp.route('/tutores', methods=['GET', 'POST'])
@login_required
def tutores():
    form = TutorForm()
    if request.args.get('busca'):
        termo = request.args.get('busca', '').strip()
        tutores_lista = []
        cpf = validar_cpf(termo)
        if cpf:
            tutores_query = db.select(Tutor).where(Tutor.cpf_hmac == cpf_hmac(cpf))
        else:
            padrao = f'%{termo}%'
            tutores_query = db.select(Tutor).where(
                or_(Tutor.nome.ilike(padrao), Tutor.telefone.ilike(padrao), Tutor.email.ilike(padrao))
            ).order_by(Tutor.nome)
    else:
        tutores_query = db.select(Tutor).order_by(Tutor.nome)

    paginacao_tutores = db.paginate(tutores_query, page=request.args.get('page', 1, type=int), per_page=10)
    tutores_lista = paginacao_tutores.items
    if request.args.get('busca') and not tutores_lista:
        flash('Nenhum tutor encontrado.', 'warning')

    if form.validate_on_submit():
        cpf = validar_cpf(form.cpf.data)
        if not cpf:
            flash('Informe um CPF válido.', 'danger')
        else:
            hmac_cpf = cpf_hmac(cpf)
            if db.session.scalar(db.select(Tutor).where(Tutor.cpf_hmac == hmac_cpf)):
                flash('Já existe um tutor cadastrado com este CPF.', 'danger')
            else:
                cpf_criptografado, nonce, tag = criptografar_cpf(cpf)
                tutor = Tutor(nome=form.nome.data.strip(), cpf_criptografado=cpf_criptografado,
                    cpf_nonce=nonce, cpf_tag=tag, cpf_hmac=hmac_cpf,
                    telefone=form.telefone.data.strip(), email=form.email.data.strip() or None,
                    endereco=form.endereco.data.strip() or None)
                db.session.add(tutor)
                db.session.flush()
                registrar_auditoria('CADASTRAR', 'tutores', tutor.id_tutor, 'Tutor cadastrado.')
                db.session.commit()
                flash('Tutor cadastrado com sucesso.', 'success')
                return redirect(url_for('main.tutores'))
    return render_template('tutores.html', form=form, tutores=tutores_lista, paginacao=paginacao_tutores,
        mascarar_cpf=mascarar_cpf, descriptografar_cpf=descriptografar_cpf)


@main_bp.route('/tutores/<int:id_tutor>/editar', methods=['POST'])
@login_required
def editar_tutor(id_tutor):
    tutor = db.session.get(Tutor, id_tutor)
    if not tutor:
        flash('Tutor não encontrado.', 'danger')
        return redirect(url_for('main.tutores'))
    form = TutorForm()
    if form.validate_on_submit():
        cpf = validar_cpf(form.cpf.data)
        if not cpf:
            flash('Informe um CPF válido.', 'danger')
            return redirect(url_for('main.tutores'))
        novo_hmac = cpf_hmac(cpf)
        existente = db.session.scalar(db.select(Tutor).where(Tutor.cpf_hmac == novo_hmac, Tutor.id_tutor != id_tutor))
        if existente:
            flash('Já existe outro tutor com este CPF.', 'danger')
            return redirect(url_for('main.tutores'))
        cpf_criptografado, nonce, tag = criptografar_cpf(cpf)
        tutor.nome = form.nome.data.strip()
        tutor.cpf_criptografado = cpf_criptografado
        tutor.cpf_nonce = nonce
        tutor.cpf_tag = tag
        tutor.cpf_hmac = novo_hmac
        tutor.telefone = form.telefone.data.strip()
        tutor.email = form.email.data.strip() or None
        tutor.endereco = form.endereco.data.strip() or None
        tutor.atualizado_em = datetime.utcnow()
        registrar_auditoria('EDITAR', 'tutores', id_tutor, 'Dados do tutor atualizados.')
        db.session.commit()
        flash('Tutor atualizado com sucesso.', 'success')
    else:
        flash('Revise os campos do formulário.', 'danger')
    return redirect(url_for('main.tutores'))


@main_bp.route('/pets', methods=['GET', 'POST'])
@login_required
def pets():
    form = PetForm()
    form.id_tutor.choices = [(t.id_tutor, t.nome) for t in db.session.scalars(db.select(Tutor).order_by(Tutor.nome)).all()]
    busca = request.args.get('busca', '').strip()
    if busca:
        padrao = f'%{busca}%'
        pets_query = db.select(Pet).join(Tutor).where(
            or_(Pet.nome.ilike(padrao), Pet.especie.ilike(padrao), Pet.raca.ilike(padrao), Tutor.nome.ilike(padrao))
        ).order_by(Pet.nome)
    else:
        pets_query = db.select(Pet).order_by(Pet.nome)

    if busca:
        pets_query = db.select(Pet).join(Tutor).where(
            or_(Pet.nome.ilike(padrao), Pet.especie.ilike(padrao), Pet.raca.ilike(padrao), Tutor.nome.ilike(padrao))
        ).order_by(Pet.nome)
    paginacao_pets = db.paginate(pets_query, page=request.args.get('page', 1, type=int), per_page=10)
    pets_lista = paginacao_pets.items
    if busca and not pets_lista:
        flash('Nenhum pet encontrado.', 'warning')

    if form.validate_on_submit():
        tutor = db.session.get(Tutor, form.id_tutor.data)
        if not tutor:
            flash('Selecione um tutor válido.', 'danger')
        else:
            pet = Pet(nome=form.nome.data.strip(), especie=form.especie.data.strip(), raca=form.raca.data.strip(),
                sexo=form.sexo.data, data_nascimento=form.data_nascimento.data,
                observacoes=form.observacoes.data.strip() or None, id_tutor=tutor.id_tutor)
            db.session.add(pet)
            db.session.flush()
            registrar_auditoria('CADASTRAR', 'pets', pet.id_pet, 'Pet cadastrado e associado a tutor.')
            db.session.commit()
            flash('Pet cadastrado com sucesso.', 'success')
            return redirect(url_for('main.pets'))
    return render_template('pets.html', form=form, pets=pets_lista, paginacao=paginacao_pets,
        tutores=db.session.scalars(db.select(Tutor).order_by(Tutor.nome)).all())


@main_bp.route('/pets/<int:id_pet>/editar', methods=['POST'])
@login_required
def editar_pet(id_pet):
    pet = db.session.get(Pet, id_pet)
    if not pet:
        flash('Pet não encontrado.', 'danger')
        return redirect(url_for('main.pets'))
    form = PetForm()
    form.id_tutor.choices = [(t.id_tutor, t.nome) for t in db.session.scalars(db.select(Tutor).order_by(Tutor.nome)).all()]
    if form.validate_on_submit():
        pet.nome = form.nome.data.strip()
        pet.especie = form.especie.data.strip()
        pet.raca = form.raca.data.strip()
        pet.sexo = form.sexo.data
        pet.data_nascimento = form.data_nascimento.data
        pet.observacoes = form.observacoes.data.strip() or None
        pet.id_tutor = form.id_tutor.data
        registrar_auditoria('EDITAR', 'pets', id_pet, 'Dados do pet atualizados.')
        db.session.commit()
        flash('Pet atualizado com sucesso.', 'success')
    else:
        flash('Revise os campos do formulário.', 'danger')
    return redirect(url_for('main.pets'))


@main_bp.route('/agendamentos', methods=['GET', 'POST'])
@login_required
def agendamentos():
    form = AgendamentoForm()
    form.id_pet.choices = [(p.id_pet, f'{p.nome} - {p.tutor.nome}') for p in db.session.scalars(db.select(Pet).order_by(Pet.nome)).all()]
    if form.validate_on_submit():
        data = form.data_agendamento.data
        if data and data < datetime.now():
            flash('Não é permitido agendar para uma data passada.', 'danger')
            return redirect(url_for('main.agendamentos'))
        conflito = db.session.scalar(db.select(Agendamento).where(
            Agendamento.id_pet == form.id_pet.data,
            Agendamento.data_agendamento == data,
            Agendamento.status != 'Cancelado',
        ))
        if conflito:
            flash('Já existe um agendamento ativo para este pet nesse horário.', 'danger')
            return redirect(url_for('main.agendamentos'))
        agendamento = Agendamento(id_pet=form.id_pet.data, data_agendamento=data,
            observacao=form.observacao.data.strip() or None, status=form.status.data)
        db.session.add(agendamento)
        db.session.flush()
        registrar_auditoria('CADASTRAR', 'agendamentos', agendamento.id_agendamento, 'Agendamento cadastrado.')
        db.session.commit()
        flash('Agendamento criado com sucesso.', 'success')
        return redirect(url_for('main.agendamentos'))
    agendamento_query = db.select(Agendamento)
    status = request.args.get('status', '').strip()
    periodo = request.args.get('periodo', '').strip()
    if status:
        agendamento_query = agendamento_query.where(Agendamento.status == status)
    if periodo:
        inicio = datetime.strptime(periodo, '%Y-%m-%d')
        agendamento_query = agendamento_query.where(
            Agendamento.data_agendamento >= inicio,
            Agendamento.data_agendamento < inicio.replace(hour=23, minute=59, second=59),
        )
    agendamento_query = agendamento_query.order_by(Agendamento.data_agendamento.asc())
    paginacao_agendamentos = db.paginate(agendamento_query, page=request.args.get('page', 1, type=int), per_page=10)
    lista = paginacao_agendamentos.items
    return render_template('agendamentos.html', form=form, agendamentos=lista,
        paginacao=paginacao_agendamentos)


@main_bp.route('/agendamentos/<int:id_agendamento>/editar', methods=['POST'])
@login_required
def editar_agendamento(id_agendamento):
    agendamento = db.session.get(Agendamento, id_agendamento)
    if not agendamento:
        flash('Agendamento não encontrado.', 'danger')
        return redirect(url_for('main.agendamentos'))
    form = AgendamentoForm()
    form.id_pet.choices = [(p.id_pet, f'{p.nome} - {p.tutor.nome}') for p in db.session.scalars(db.select(Pet).order_by(Pet.nome)).all()]
    if form.validate_on_submit():
        data = form.data_agendamento.data
        if data and data < datetime.now():
            flash('Não é permitido agendar para uma data passada.', 'danger')
            return redirect(url_for('main.agendamentos'))
        conflito = db.session.scalar(db.select(Agendamento).where(
            Agendamento.id_agendamento != id_agendamento,
            Agendamento.id_pet == form.id_pet.data,
            Agendamento.data_agendamento == data,
            Agendamento.status != 'Cancelado',
        ))
        if conflito:
            flash('Já existe um agendamento ativo para este pet nesse horário.', 'danger')
            return redirect(url_for('main.agendamentos'))
        agendamento.id_pet = form.id_pet.data
        agendamento.data_agendamento = data
        agendamento.observacao = form.observacao.data.strip() or None
        agendamento.status = form.status.data
        agendamento.atualizado_em = datetime.utcnow()
        registrar_auditoria('EDITAR', 'agendamentos', id_agendamento, 'Agendamento atualizado.')
        db.session.commit()
        flash('Agendamento atualizado com sucesso.', 'success')
    else:
        flash('Revise os campos do agendamento.', 'danger')
    return redirect(url_for('main.agendamentos'))


@main_bp.route('/auditoria')
@login_required
def auditoria():
    if getattr(current_user, 'perfil', 'atendimento') != 'administrador':
        flash('Você não possui permissão para acessar a auditoria.', 'danger')
        return redirect(url_for('main.dashboard'))
    acao = request.args.get('acao', '').strip()
    data = request.args.get('data', '').strip()
    consulta = db.select(Auditoria).order_by(Auditoria.data_hora.desc())
    if acao:
        consulta = consulta.where(Auditoria.acao.ilike(f'%{acao}%'))
    if data:
        inicio = datetime.strptime(data, '%Y-%m-%d')
        fim = inicio + timedelta(days=1)
        consulta = consulta.where(Auditoria.data_hora >= inicio, Auditoria.data_hora < fim)
    paginacao_auditoria = db.paginate(consulta, page=request.args.get('page', 1, type=int), per_page=15)
    usuarios = {u.id_usuario: u.nome for u in db.session.scalars(db.select(Usuario)).all()}
    return render_template('auditoria.html', registros=paginacao_auditoria.items,
        paginacao=paginacao_auditoria, usuarios=usuarios)
