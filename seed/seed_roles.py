r"""
seed_roles.py
-------------
WHAT: Inserts the USER and ADMIN rows into the roles table if they don't
      already exist.
WHY:  Registration (app/routes/auth.py) looks up the USER role and fails
      gracefully if it's missing — so this must run once before anyone
      can register.
WHERE: seed/seed_roles.py
HOW TO RUN (Windows, from the project root, venv activated):
    python seed\seed_roles.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.role import ROLE_ADMIN, ROLE_USER, Role


def run():
    app = create_app(os.environ.get("FLASK_CONFIG", "development"))
    with app.app_context():
        created = []
        for role_name in (ROLE_USER, ROLE_ADMIN):
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))
                created.append(role_name)
        db.session.commit()

        if created:
            print(f"Seeded roles: {', '.join(created)}")
        else:
            print("Roles already exist — nothing to do.")


if __name__ == "__main__":
    run()
