"""
role.py
-------
WHAT: The `roles` table — just two rows in practice: USER and ADMIN.
WHY:  Role-based access control (RBAC). Instead of a boolean "is_admin" flag,
      a proper roles table is easier to extend later (e.g. a MODERATOR role)
      and is the pattern expected by the project spec.
WHERE: app/models/role.py
HOW:  Seeded once via seed/seed_roles.py (Phase 1) — see that file.
"""

from app.extensions import db

ROLE_USER = "USER"
ROLE_ADMIN = "ADMIN"


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name}>"
