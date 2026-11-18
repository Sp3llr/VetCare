import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from sqlalchemy import event

from config import Config


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

@login_manager.unauthorized_handler
def unauthorized():
    from flask import redirect, url_for, flash
    flash('Faça login para acessar o sistema.', 'warning')
    return redirect(url_for('auth.login'))


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    @app.before_request
    def log_before_request():
        return None

    with app.app_context():
        from . import models

        @event.listens_for(db.engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()

        db.create_all()

        try:
            from sqlalchemy import text
            colunas = db.session.execute(text("PRAGMA table_info(usuarios)")).fetchall()
            if 'perfil' not in {coluna[1] for coluna in colunas}:
                db.session.execute(text("ALTER TABLE usuarios ADD COLUMN perfil VARCHAR(30) NOT NULL DEFAULT 'atendimento'"))
                db.session.execute(text("UPDATE usuarios SET perfil = 'administrador' WHERE login = 'ana'"))
                db.session.commit()
        except Exception:
            db.session.rollback()

    @app.after_request
    def aplicar_cabecalhos_seguranca(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'geolocation=(), camera=(), microphone=()')
        return response

    from .auth import auth_bp
    from .routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
