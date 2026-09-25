"""
learning_content.py
--------------------
WHAT: Short beginner-friendly lessons for the Cyber Safety Learning Center
      (Part G). Each has the What/Warning-signs/Example/What-to-do shape.
WHERE: app/models/learning_content.py
"""

from app.extensions import db


class LearningContent(db.Model):
    __tablename__ = "learning_content"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g. "phishing", "mfa"
    title = db.Column(db.String(120), nullable=False)

    what_is_it = db.Column(db.Text, nullable=False)
    warning_signs = db.Column(db.Text, nullable=False)   # newline-separated bullets
    example = db.Column(db.Text, nullable=False)
    what_to_do = db.Column(db.Text, nullable=False)

    order_index = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<LearningContent {self.key}>"
