# VetCare - Sistema Veterinário LGPD

Sistema web completo em Python/Flask para cadastro de tutores, pets e agendamentos, com SQLite, criptografia AES-256-GCM, HMAC-SHA-256 e auditoria.

## Requisitos

- Python 3.11 ou superior
- Navegador moderno
- Windows ou Linux

## Instalação no Windows

```powershell
cd C:\Users\ALUNOS\Desktop\Sistema
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

## Instalação no Linux

```bash
cd /caminho/Sistema
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Configuração das chaves

Gere duas chaves independentes de 32 bytes em base64 URL-safe:

```bash
python -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

Repita o comando e configure `CPF_AES_KEY` e `CPF_HMAC_KEY` no `.env`. Configure também `SECRET_KEY`. Não use os valores de exemplo diretamente em produção.

## Inicializar e popular o banco

```bash
python scripts/seed.py
```

## Executar

```bash
python run.py
```

Acesse `http://127.0.0.1:5000`.

## Credenciais de demonstração

- Usuário: `ana` / Senha: `Vet@2026`
- Usuário: `bruno` / Senha: `Vet@2026`
- Usuário: `carla` / Senha: `Vet@2026`

## Segurança

- Senhas com hash `Werkzeug`.
- Sessão expira após 20 minutos de inatividade e 8 horas absolutas.
- Bloqueio após cinco falhas de login por 15 minutos.
- CSRF habilitado pelo Flask-WTF.
- Cookies `HttpOnly`, `SameSite=Lax` e `Secure` em produção.
- CPF validado, criptografado com AES-256-GCM e pesquisável por HMAC-SHA-256 separado.
- CPF exibido somente mascarado.
- `PRAGMA foreign_keys=ON` em todas as conexões SQLite.
- Operações relevantes registradas na auditoria.

## LGPD

Os dados pessoais são coletados para identificação do tutor, contato e prestação de serviços veterinários. O CPF é armazenado criptografado e exibido mascarado. Solicitações de acesso, correção ou exclusão devem ser validadas pelo responsável pelo tratamento antes da ação administrativa. Registros relacionados não são excluídos automaticamente quando possuem dependências.

## Backup do banco

```bash
python scripts/backup.py
```

Uma cópia SQLite consistente será criada em `instance/backups/`.

## Restauração do banco

```bash
python scripts/restore.py instance/backups/NOME_DO_BACKUP.db
```

A restauração substitui o banco atual. Faça novo backup antes de restaurar.

## Cadastro e perfis

O cadastro público cria usuários com perfil `atendimento`. O perfil `administrador` é reservado às contas existentes e tem acesso à auditoria.

## Filtros e interface

Tutores, pets e agendamentos possuem paginação e pesquisa onde aplicável. Agendamentos podem ser filtrados por status e período. A interface usa identidade azul-turquesa, logo VetCare, ripple e ondas de autenticação.

## Testes

```bash
pytest -q
```
