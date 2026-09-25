r"""
create_admin.py
----------------
WHAT: Interactive CLI script that creates (or promotes) an ADMIN account.
WHY:  The spec requires admin credentials to be securely PROMPTED, never
      hard-coded anywhere in source control.
WHERE: scripts/create_admin.py
HOW TO RUN (Windows, from the project root, venv activated):
    python scripts\create_admin.py

The password is entered with getpass (hidden input, not echoed to the
terminal, and never appears in shell history).
"""

import getpass
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.role import ROLE_ADMIN, Role
from app.models.user import User
from app.utils.security import password_strength_errors

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def prompt_username() -> str:
    while True:
        username = input("Admin username: ").strip()
        if 3 <= len(username) <= 30 and re.fullmatch(r"[A-Za-z0-9_]+", username):
            return username
        print("Username must be 3-30 characters: letters, numbers, underscores only.")


def prompt_email() -> str:
    while True:
        email = input("Admin email: ").strip().lower()
        if EMAIL_RE.match(email):
            return email
        print("That doesn't look like a valid email address.")


def prompt_password(username: str, email: str) -> str:
    while True:
        password = getpass.getpass("Admin password (hidden): ")
        confirm = getpass.getpass("Confirm password (hidden): ")
        if password != confirm:
            print("Passwords did not match. Try again.\n")
            continue
        errors = password_strength_errors(password, username=username, email=email)
        if errors:
            print("Password is not strong enough:")
            for e in errors:
                print(f"  - {e}")
            print()
            continue
        return password


def run():
    app = create_app(os.environ.get("FLASK_CONFIG", "development"))
    with app.app_context():
        admin_role = Role.query.filter_by(name=ROLE_ADMIN).first()
        if admin_role is None:
            print("ERROR: ADMIN role not found. Run 'python seed/seed_roles.py' first.")
            sys.exit(1)

        print("=== CyberShield: Create Admin Account ===")
        username = prompt_username()
        email = prompt_email()

        existing = User.query.filter(
            db.or_(
                db.func.lower(User.username) == username.lower(),
                db.func.lower(User.email) == email,
            )
        ).first()
        if existing:
            confirm = input(
                f"A user '{existing.username}' already exists with that username/email. "
                f"Promote it to ADMIN instead? [y/N]: "
            ).strip().lower()
            if confirm == "y":
                existing.role = admin_role
                db.session.commit()
                print(f"'{existing.username}' is now an ADMIN.")
            else:
                print("Aborted. No changes made.")
            return

        password = prompt_password(username, email)

        admin_user = User(username=username, email=email, role=admin_role)
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()

        print(f"Admin account '{username}' created successfully.")


if __name__ == "__main__":
    run()
