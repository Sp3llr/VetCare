import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DESTINO = BASE_DIR / 'instance' / 'sistema_veterinario.db'


def restaurar(origem):
    origem = Path(origem)
    if not origem.is_file():
        raise FileNotFoundError('Arquivo de backup não encontrado.')
    if origem.suffix != '.db':
        raise ValueError('O backup deve ser um arquivo SQLite .db.')
    shutil.copy2(origem, DESTINO)
    print(f'Banco restaurado em {DESTINO}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python scripts/restore.py CAMINHO_DO_BACKUP.db')
    restaurar(sys.argv[1])
