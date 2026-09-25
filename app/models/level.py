"""
level.py
--------
WHAT: The 5 fixed training levels (Phishing Hunter, URL Detective,
      Account Guardian, Scam Spotter, Cyber Escape).
WHERE: app/models/level.py
"""

from app.extensions import db

LEVEL_KEYS = [
    "phishing_hunter",
    "url_detective",
    "account_guardian",
    "scam_spotter",
    "cyber_escape",
]


class Level(db.Model):
    __tablename__ = "levels"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)  # 1-5
    key = db.Column(db.String(30), unique=True, nullable=False)  # e.g. "phishing_hunter"
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    challenges = db.relationship(
        "Challenge", back_populates="level", order_by="Challenge.order_index",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Level {self.number}:{self.key}>"
