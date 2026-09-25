"""
forms.py
--------
WHAT: WTForms classes for register/login. Flask-WTF wires in CSRF
      protection automatically for every form defined this way.
WHY:  Server-side validation (length, format, required fields) must never
      be skipped just because the browser also validates — an attacker
      can bypass browser JS entirely.
WHERE: app/routes/forms.py
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=30),
            Regexp(r"^[A-Za-z0-9_]+$", message="Letters, numbers, and underscores only."),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=10)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    identifier = StringField(
        "Username or Email", validators=[DataRequired(), Length(max=255)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me signed in")
    submit = SubmitField("Log in")
