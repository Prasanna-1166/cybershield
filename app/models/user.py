"""
user.py
-------
WHAT: The `users` table plus password hashing helpers.
WHY:  Central identity record for the whole platform. Every other table
      (attempts, scores, badges, reports, ...) added in later phases will
      have a foreign key pointing back to users.id.
WHERE: app/models/user.py
HOW:  Passwords are NEVER stored in plaintext. We use Werkzeug's
      generate_password_hash / check_password_hash, which salts and hashes
      with PBKDF2-SHA256 by default — this ships with Flask itself, so
      there's no extra native dependency to install on Windows.
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.role import ROLE_USER


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Login identity
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # Never store plaintext or even a reversible form of the password.
    password_hash = db.Column(db.String(255), nullable=False)

    # Shown on leaderboards instead of username/email if the user sets one.
    display_name = db.Column(db.String(50), nullable=True)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", back_populates="users")

    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at = db.Column(db.DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------
    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # ------------------------------------------------------------------
    # Flask-Login integration
    # ------------------------------------------------------------------
    # UserMixin already provides is_authenticated / is_anonymous / get_id().
    # We override is_active so a deactivated account can't log in even with
    # the correct password.
    @property
    def is_active(self):
        return self.is_active_account

    # ------------------------------------------------------------------
    # Role helpers
    # ------------------------------------------------------------------
    @property
    def is_admin(self) -> bool:
        return self.role is not None and self.role.name == "ADMIN"

    def display(self) -> str:
        """Name shown in UI (leaderboard, dashboard) — never the email."""
        return self.display_name or self.username

    def __repr__(self):
        return f"<User {self.username}>"


def default_role_name() -> str:
    """Used by the registration form so new sign-ups are USER, never ADMIN."""
    return ROLE_USER
