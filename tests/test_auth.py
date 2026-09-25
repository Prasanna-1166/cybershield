"""
test_auth.py
------------
Exercises the full register -> login -> access dashboard -> logout flow,
plus a few security-relevant edge cases (duplicate accounts, wrong
password, protected route without login).

Uses TestingConfig (in-memory SQLite) — see app/config.py. This is a
TEST-ONLY substitution so the suite is fast and never touches the real
MySQL database; the shipped app still targets MySQL.

Run with (venv activated, dependencies installed):
    python -m unittest tests.test_auth -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.role import ROLE_ADMIN, ROLE_USER, Role


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        db.session.add(Role(name=ROLE_USER))
        db.session.add(Role(name=ROLE_ADMIN))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def register(self, username="alice", email="alice@example.com",
                 password="Str0ng!Passw0rd", confirm=None):
        return self.client.post(
            "/auth/register",
            data={
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": confirm if confirm is not None else password,
            },
            follow_redirects=True,
        )

    def login(self, identifier="alice", password="Str0ng!Passw0rd"):
        return self.client.post(
            "/auth/login",
            data={"identifier": identifier, "password": password},
            follow_redirects=True,
        )

    # ------------------------------------------------------------------

    def test_register_then_login_succeeds(self):
        resp = self.register()
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"You can now log in", resp.data)

        resp = self.login()
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Welcome back", resp.data)

    def test_duplicate_email_is_rejected(self):
        self.register(username="alice", email="dup@example.com")
        resp = self.register(username="alice2", email="dup@example.com")
        self.assertIn(b"already registered", resp.data)

    def test_weak_password_is_rejected(self):
        resp = self.register(password="weak", confirm="weak")
        # Should NOT create the account or redirect to login-success flow.
        self.assertNotIn(b"You can now log in", resp.data)

    def test_wrong_password_shows_generic_error(self):
        self.register()
        resp = self.login(password="TotallyWrongPassword!1")
        self.assertIn(b"Invalid username/email or password", resp.data)

    def test_dashboard_requires_login(self):
        resp = self.client.get("/dashboard", follow_redirects=True)
        self.assertIn(b"Please log in", resp.data)

    def test_dashboard_accessible_after_login(self):
        self.register()
        self.login()
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"alice", resp.data)
        self.assertIn(b"Welcome back", resp.data)

    def test_logout_clears_session(self):
        self.register()
        self.login()
        self.client.get("/auth/logout")
        resp = self.client.get("/dashboard", follow_redirects=True)
        self.assertIn(b"Please log in", resp.data)


if __name__ == "__main__":
    unittest.main()
