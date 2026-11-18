import os
import secrets
import base64
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)


def garantir_chaves_persistentes():
    """Cria chaves uma única vez para que dados cifrados sobrevivam a reinícios."""
    valores = {
        'SECRET_KEY': os.getenv('SECRET_KEY') or secrets.token_urlsafe(48),
        'CPF_AES_KEY': os.getenv('CPF_AES_KEY') or base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        'CPF_HMAC_KEY': os.getenv('CPF_HMAC_KEY') or base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
    }

    for nome, valor in valores.items():
        os.environ[nome] = valor

    if not ENV_FILE.exists():
        linhas = [f'{nome}={valor}' for nome, valor in valores.items()]
        linhas.append('FLASK_ENV=development')
        ENV_FILE.write_text('\n'.join(linhas) + '\n', encoding='utf-8')


garantir_chaves_persistentes()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
