import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'sistema_veterinario.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    PERMANENT_SESSION_LIFETIME = 1200
    WTF_CSRF_TIME_LIMIT = None
    CPF_AES_KEY = os.getenv('CPF_AES_KEY')
    CPF_HMAC_KEY = os.getenv('CPF_HMAC_KEY')
