"""
security.py
------------
WHAT: Small, dependency-free security helper functions.
WHY:  Keeps password-strength rules in one testable place instead of
      scattered inside route handlers or templates.
WHERE: app/utils/security.py
HOW:  Called from app/routes/auth.py during registration. Pure Python,
      no Flask/DB imports, so it's trivial to unit-test in isolation
      (see tests/test_password_strength.py).
"""

import re

MIN_LENGTH = 10

# A short blocklist of extremely common password ROOTS. Not exhaustive —
# it's an educational baseline, not a replacement for a real breach-list API.
# We match against the "root" (letters only, lowercased) so decorated
# variants like "Password1!" or "Welcome123$" are still caught, not just
# the bare word.
COMMON_PASSWORD_ROOTS = {
    "password", "qwerty", "letmein", "welcome", "iloveyou",
    "admin", "monkey", "dragon", "football", "baseball", "trustno1",
}


def password_strength_errors(password: str, username: str = "", email: str = "") -> list[str]:
    """
    Returns a list of human-readable problems with `password`.
    An empty list means the password passes all checks.
    """
    errors = []

    if len(password) < MIN_LENGTH:
        errors.append(f"Password must be at least {MIN_LENGTH} characters long.")

    if not re.search(r"[a-z]", password):
        errors.append("Password must include at least one lowercase letter.")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must include at least one uppercase letter.")

    if not re.search(r"\d", password):
        errors.append("Password must include at least one number.")

    if not re.search(r"[^\w\s]", password):
        errors.append("Password must include at least one symbol (e.g. ! @ # $ %).")

    letters_only_root = re.sub(r"[^a-z]", "", password.lower())
    if letters_only_root in COMMON_PASSWORD_ROOTS or any(
        letters_only_root.startswith(root) for root in COMMON_PASSWORD_ROOTS
    ):
        errors.append("This password is far too common — choose something more unique.")

    lowered = password.lower()
    if username and username.lower() in lowered and len(username) >= 4:
        errors.append("Password must not contain your username.")
    if email:
        local_part = email.split("@")[0].lower()
        if len(local_part) >= 4 and local_part in lowered:
            errors.append("Password must not contain your email address.")

    return errors


def is_strong_password(password: str, username: str = "", email: str = "") -> bool:
    return len(password_strength_errors(password, username, email)) == 0
