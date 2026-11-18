import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ORIGEM = BASE_DIR / 'instance' / 'sistema_veterinario.db'
DESTINO = BASE_DIR / 'instance' / 'backups'


def criar_backup():
    if not ORIGEM.exists():
        raise FileNotFoundError('Banco SQLite não encontrado.')
    DESTINO.mkdir(parents=True, exist_ok=True)
    nome = f"sistema_veterinario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = DESTINO / nome
    with sqlite3.connect(ORIGEM) as origem, sqlite3.connect(destino) as copia:
        origem.backup(copia)
    print(destino)
    return destino


if __name__ == '__main__':
    criar_backup()
