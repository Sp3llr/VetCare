import base64
import hashlib
import hmac
import re
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import current_app


def _key(name):
    raw = current_app.config.get(name)
    if not raw:
        raise RuntimeError(f'Variável de ambiente {name} não configurada.')
    return base64.urlsafe_b64decode(raw.encode() + b'=' * (-len(raw) % 4))


def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf or '')
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return None
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    if digito1 != int(cpf[9]):
        return None
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    if digito2 != int(cpf[10]):
        return None
    return cpf


def criptografar_cpf(cpf):
    cpf = validar_cpf(cpf)
    if not cpf:
        raise ValueError('CPF inválido.')
    key = _key('CPF_AES_KEY')
    if len(key) != 32:
        raise RuntimeError('A chave AES deve conter 32 bytes.')
    nonce_bytes = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    ciphertext_tag = aesgcm.encrypt(nonce_bytes, cpf.encode(), None)
    ciphertext = ciphertext_tag[:-16]
    tag = ciphertext_tag[-16:]
    return (
        base64.b64encode(ciphertext).decode(),
        base64.b64encode(nonce_bytes).decode(),
        base64.b64encode(tag).decode(),
    )


def descriptografar_cpf(tutor):
    try:
        key = _key('CPF_AES_KEY')
        nonce = base64.b64decode(tutor.cpf_nonce)
        ciphertext = base64.b64decode(tutor.cpf_criptografado)
        tag = base64.b64decode(tutor.cpf_tag)
        return AESGCM(key).decrypt(nonce, ciphertext + tag, None).decode()
    except (InvalidTag, ValueError, TypeError, RuntimeError):
        return None


def cpf_hmac(cpf):
    cpf = validar_cpf(cpf)
    if not cpf:
        raise ValueError('CPF inválido.')
    key = _key('CPF_HMAC_KEY')
    if len(key) < 32:
        raise RuntimeError('A chave HMAC deve conter pelo menos 32 bytes.')
    return hmac.new(key, cpf.encode(), hashlib.sha256).hexdigest()


def mascarar_cpf(cpf):
    if not cpf:
        return '***.***.***-*'
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        return '***.***.***-*'
    return f'***.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
