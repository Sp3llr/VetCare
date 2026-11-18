from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo, Regexp


class LoginForm(FlaskForm):
    login = StringField('Usuário', validators=[DataRequired(), Length(max=80)])
    senha = PasswordField('Senha', validators=[DataRequired()])


class CadastroForm(FlaskForm):
    nome = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=150)])
    login = StringField('Usuário', validators=[
        DataRequired(), Length(min=3, max=80),
        Regexp(r'^[A-Za-z0-9_.-]+$', message='Use apenas letras, números, ponto, hífen ou underline.'),
    ])
    senha = PasswordField('Senha', validators=[
        DataRequired(), Length(min=8, max=128),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d).+$', message='A senha deve conter letras e números.'),
    ])
    confirmar_senha = PasswordField('Confirmar senha', validators=[
        DataRequired(), EqualTo('senha', message='As senhas não coincidem.'),
    ])


class TutorForm(FlaskForm):
    nome = StringField('Nome completo', validators=[DataRequired(), Length(max=150)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(max=14)])
    telefone = StringField('Telefone', validators=[DataRequired(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=150)])
    endereco = StringField('Endereço', validators=[Optional(), Length(max=255)])


class PetForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    especie = StringField('Espécie', validators=[DataRequired(), Length(max=50)])
    raca = StringField('Raça', validators=[DataRequired(), Length(max=100)])
    sexo = SelectField('Sexo', choices=[('Macho', 'Macho'), ('Fêmea', 'Fêmea')], validators=[DataRequired()])
    data_nascimento = DateField('Data de nascimento', validators=[DataRequired()], format='%Y-%m-%d')
    observacoes = TextAreaField('Observações', validators=[Optional()])
    id_tutor = SelectField('Tutor responsável', coerce=int, validators=[DataRequired()])


class AgendamentoForm(FlaskForm):
    id_pet = SelectField('Pet', coerce=int, validators=[DataRequired()])
    data_agendamento = DateTimeLocalField('Data e horário', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    observacao = TextAreaField('Observações', validators=[Optional()])
    status = SelectField('Status', choices=[('Agendado', 'Agendado'), ('Confirmado', 'Confirmado'), ('Concluído', 'Concluído'), ('Cancelado', 'Cancelado')])
