"""
test_config_and_health.py
--------------------------
Covers two things added in the deployment/security hardening pass:

1. GET /health — used by hosting platforms and uptime monitors.
2. ProductionConfig.validate() — the app must refuse to start in production
   without a real SECRET_KEY, rather than silently running insecurely.

Run with: python -m unittest tests.test_config_and_health -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db


class HealthEndpointTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_health_returns_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_health_does_not_require_login(self):
        # No session/cookies set up — must still succeed.
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)


class SecurityHeaderTests(unittest.TestCase):
    """Uses /health (no DB dependency) to isolate header behavior from the
    home page's own database-backed tests elsewhere in the suite."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_security_headers_present(self):
        response = self.client.get("/health")
        self.assertIn("Content-Security-Policy", response.headers)
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")

    def test_csp_nonce_changes_per_request(self):
        first = self.client.get("/health").headers.get("Content-Security-Policy")
        second = self.client.get("/health").headers.get("Content-Security-Policy")
        self.assertNotEqual(first, second)


class ProductionConfigSafetyTests(unittest.TestCase):
    def setUp(self):
        self._original_secret = os.environ.pop("SECRET_KEY", None)

    def tearDown(self):
        if self._original_secret is not None:
            os.environ["SECRET_KEY"] = self._original_secret

    def test_missing_secret_key_refuses_to_start(self):
        with self.assertRaises(RuntimeError):
            create_app("production")

    def test_default_placeholder_secret_key_refuses_to_start(self):
        os.environ["SECRET_KEY"] = "dev-only-insecure-key-change-me"
        with self.assertRaises(RuntimeError):
            create_app("production")


if __name__ == "__main__":
    unittest.main()
