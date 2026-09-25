"""
config.py
---------
WHAT: Defines app settings (secret key, database URL, cookie rules, etc.)
      as Python classes, one per environment (development / testing / production).
WHY:  Keeps secrets and environment-specific values OUT of source code.
      Nothing here is hard-coded — every sensitive value is read from
      environment variables (loaded from a local ".env" file via python-dotenv).
WHERE: app/config.py
HOW:  app/__init__.py picks a config class by name and applies it to the Flask app.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Load variables from a .env file (if present) into the process environment.
# This must happen before we read os.environ.get(...) below.
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(basedir, ".env"))


class BaseConfig:
    """Settings shared by every environment."""

    # --- Secrets ---------------------------------------------------------
    # SECRET_KEY signs session cookies and CSRF tokens. It MUST come from
    # the environment. We deliberately do not provide a real default here —
    # if it's missing in production that's a configuration bug we want to
    # surface, not silently paper over with a guessable fallback.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

    # --- Database ------------------------------------------------------------
    # Default: a local SQLite file under instance/ — zero setup, no server to
    # install or run. Point DATABASE_URL at Postgres (or MySQL) later without
    # touching any model code, e.g.:
    #   DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
    _default_sqlite_path = os.path.join(basedir, "instance", "cybershield.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{_default_sqlite_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # pool_pre_ping avoids stale-connection errors on server-based databases
    # (Postgres/MySQL) after periods of idleness. SQLite ignores pooling
    # options, so this is safe to leave on for every backend.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # --- Sessions / cookies -------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True          # JS on the page cannot read the session cookie
    SESSION_COOKIE_SAMESITE = "Lax"         # basic CSRF/clickjacking mitigation
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # --- CSRF (Flask-WTF) ----------------------------------------------------
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # tokens valid for the whole session, not just 1 hour

    # --- Rate limiting (Flask-Limiter) --------------------------------------
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

    # --- Misc ---------------------------------------------------------------
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # In dev it's fine to run over plain HTTP on localhost.
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    """Used by the automated test suite (tests/). Uses an in-memory SQLite DB
    so tests are fast and never touch the real MySQL database. This is a
    TEST-ONLY substitution — the shipped application still targets MySQL."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # simplifies posting test forms without a token
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def validate(cls) -> None:
        """Fail loudly at startup rather than silently running an insecure
        production deployment. Called explicitly by create_app() when
        FLASK_CONFIG=production — NOT called for development/testing."""
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key or secret_key == "dev-only-insecure-key-change-me":
            raise RuntimeError(
                "SECRET_KEY environment variable must be set to a strong, "
                "random value in production. Generate one with: "
                "python -c \"import secrets; print(secrets.token_hex(32))\""
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
