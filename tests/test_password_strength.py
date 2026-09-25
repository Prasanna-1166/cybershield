"""
test_password_strength.py
--------------------------
Pure unit tests for app/utils/security.py — no Flask app or database needed.
Run with:  python -m unittest tests.test_password_strength -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.security import is_strong_password, password_strength_errors


class PasswordStrengthTests(unittest.TestCase):
    def test_too_short_is_rejected(self):
        self.assertFalse(is_strong_password("Ab1!"))

    def test_all_lowercase_is_rejected(self):
        self.assertFalse(is_strong_password("alllowercase123!"))

    def test_missing_symbol_is_rejected(self):
        self.assertFalse(is_strong_password("Password12345"))

    def test_common_password_is_rejected(self):
        # Meets length/case/digit/symbol rules but the root word is "password" —
        # must still be rejected as too common.
        self.assertFalse(is_strong_password("Password1!"))

    def test_password_containing_username_is_rejected(self):
        self.assertFalse(is_strong_password("JohnSmith2024!", username="JohnSmith"))

    def test_strong_password_is_accepted(self):
        self.assertTrue(is_strong_password("Tr0ub4dor&Zebra"))
        self.assertEqual(password_strength_errors("Tr0ub4dor&Zebra"), [])


if __name__ == "__main__":
    unittest.main()
