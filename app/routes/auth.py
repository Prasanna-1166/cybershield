"""
auth.py
-------
WHAT: Register / Login / Logout routes.
WHY:  Every protected feature (game, analyzer, dashboard, admin panel) in
      later phases depends on knowing who the current user is.
WHERE: app/routes/auth.py, mounted at /auth/... in app/__init__.py
HOW TO TEST: tests/test_auth.py exercises register -> login -> logout.
             Manually: run the server, visit /auth/register.

SECURITY NOTES:
- Passwords are hashed (see app/models/user.py), never stored in plaintext.
- Login and register are rate-limited to slow down brute-force / credential
  stuffing attempts (see the @limiter.limit(...) decorators).
- Login errors are deliberately generic ("Invalid username/email or
  password") so an attacker can't use error messages to enumerate which
  usernames or emails exist in the database.
- All DB lookups go through SQLAlchemy's query API, which parameterizes
  values automatically — no raw string-built SQL anywhere in this file.
"""

from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db, limiter
from app.models.role import ROLE_USER, Role
from app.models.user import User
from app.routes.forms import LoginForm, RegisterForm
from app.utils.security import password_strength_errors

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # slows down automated account-creation abuse
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        # Extra server-side password-strength check beyond "is it 10+ chars"
        # (WTForms Length() already covers minimum length).
        strength_errors = password_strength_errors(password, username=username, email=email)
        if strength_errors:
            for err in strength_errors:
                flash(err, "danger")
            return render_template("auth/register.html", form=form)

        # Case-insensitive uniqueness check.
        existing = User.query.filter(
            db.or_(
                db.func.lower(User.username) == username.lower(),
                db.func.lower(User.email) == email,
            )
        ).first()
        if existing:
            flash("That username or email is already registered.", "danger")
            return render_template("auth/register.html", form=form)

        user_role = Role.query.filter_by(name=ROLE_USER).first()
        if user_role is None:
            # This should only happen if the DB wasn't seeded yet.
            flash(
                "Registration is temporarily unavailable (roles not configured). "
                "Please contact the site administrator.",
                "danger",
            )
            return render_template("auth/register.html", form=form)

        new_user = User(username=username, email=email, role=user_role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # basic brute-force throttling
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        identifier = form.identifier.data.strip().lower()
        password = form.password.data

        user = User.query.filter(
            db.or_(
                db.func.lower(User.username) == identifier,
                db.func.lower(User.email) == identifier,
            )
        ).first()

        # Deliberately generic message — do not reveal whether the
        # username/email exists or whether it was the password that failed.
        generic_error = "Invalid username/email or password."

        if user is None or not user.check_password(password):
            flash(generic_error, "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_active:
            flash("This account has been deactivated. Contact an administrator.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember_me.data)
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        flash(f"Welcome back, {user.display()}!", "success")
        next_page = request.args.get("next")
        # Only follow "next" if it's a safe relative path, to avoid
        # open-redirect attacks via a crafted ?next= value.
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
