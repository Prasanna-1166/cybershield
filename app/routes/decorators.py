"""
decorators.py
-------------
WHAT: @admin_required — enforces ADMIN role on every admin route.
WHY:  "Authorization checks on every protected route" is a hard security
      requirement. Using one decorator (instead of copy-pasted checks)
      means every admin route gets the same, correct behavior.
WHERE: app/routes/decorators.py
"""

from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped
