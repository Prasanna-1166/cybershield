"""
__init__.py (app factory)
--------------------------
WHAT: create_app() builds and configures the Flask application: config,
      extensions (DB, login, CSRF, rate limiter), blueprints, and error
      handlers.
WHY:  The "factory" pattern (instead of one global `app = Flask(__name__)`)
      lets us create multiple independent app instances with different
      configs — one for `flask run`, a fresh one for every test in
      tests/, etc. This is the standard, testable way to structure Flask.
WHERE: app/__init__.py
HOW TO RUN: see run.py at the project root, or `flask run` after setting
            FLASK_APP=run.py (see README.md Phase 1 section).
"""

import os
import secrets

from flask import Flask, g, jsonify, render_template

from app.config import ProductionConfig, config_by_name
from app.extensions import csrf, db, limiter, login_manager, migrate


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Production must fail at startup rather than run insecurely.
    if config_class is ProductionConfig:
        ProductionConfig.validate()

    # Make sure the instance/ folder (default home of the SQLite file)
    # exists before SQLAlchemy tries to open a file inside it.
    os.makedirs(app.instance_path, exist_ok=True)

    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_user_loader()
    _register_health_check(app)
    _register_security_headers(app)

    return app


def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    # Importing the models package registers every table with SQLAlchemy's
    # metadata (needed by db.create_all() / Flask-Migrate) even if a given
    # blueprint doesn't happen to import every model module itself.
    with app.app_context():
        import app.models  # noqa: F401


def _register_blueprints(app: Flask) -> None:
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.check import check_bp
    from app.routes.game import game_bp
    from app.routes.help import help_bp
    from app.routes.learn import learn_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(check_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(learn_bp)
    app.register_blueprint(admin_bp)


def _register_user_loader() -> None:
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id: str):
        # Flask-Login passes the id as a string; SQLAlchemy needs an int.
        return db.session.get(User, int(user_id))


def _register_error_handlers(app: Flask) -> None:
    """
    Friendly error pages for every status code the spec calls out.
    IMPORTANT: none of these leak a stack trace or internal detail to the
    user — that's what server-side logging (not shown to the browser) is for.
    """

    def make_handler(code: int):
        def handler(_error):
            return render_template(f"errors/{code}.html"), code

        return handler

    for status_code in (400, 401, 403, 404, 429, 500):
        app.register_error_handler(status_code, make_handler(status_code))


def _register_health_check(app: Flask) -> None:
    """A minimal, unauthenticated liveness endpoint for hosting platforms
    and uptime monitors. Deliberately reveals nothing about the database,
    config, or internals — just confirms the process is up and serving."""

    @app.route("/health")
    def health():
        return jsonify(status="ok")


def _register_security_headers(app: Flask) -> None:
    """Adds standard production security headers to every response.

    The CSP is intentionally conservative: only same-origin plus the exact
    third-party hosts the templates use. If you add a new external
    script/style/font source to a template, you must also add its host
    here or the browser will silently block it. The few inline <script>
    blocks in templates (game/play.html, dashboard/report.html) use a
    per-request nonce via {{ csp_nonce() }} instead of 'unsafe-inline'.
    """

    @app.before_request
    def _set_csp_nonce():
        g.csp_nonce = secrets.token_urlsafe(16)

    @app.context_processor
    def _inject_csp_nonce():
        return {"csp_nonce": lambda: g.get("csp_nonce", "")}

    @app.after_request
    def set_security_headers(response):
        nonce = g.get("csp_nonce", "")
        response.headers.setdefault(
            "Content-Security-Policy",
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net; "
            f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            f"font-src 'self' data:; "
            f"img-src 'self' data:; "
            f"object-src 'none'; "
            f"base-uri 'self'; "
            f"frame-ancestors 'none';",
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        return response
