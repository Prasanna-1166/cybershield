"""
extensions.py
-------------
WHAT: Creates the Flask extension objects (database, login manager, CSRF
      protection, rate limiter) WITHOUT binding them to an app yet.
WHY:  This "init then bind later" pattern avoids circular imports — models,
      routes, and the app factory can all import these objects safely.
WHERE: app/extensions.py
HOW:  app/__init__.py calls db.init_app(app), login_manager.init_app(app), etc.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()

# Where Flask-Login sends anonymous users who hit a @login_required page.
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access that page."
login_manager.login_message_category = "info"
