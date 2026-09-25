"""
challenge.py
------------
WHAT: A single game item within a level — a phishing email to inspect, a URL
      to judge, a password scenario, etc. Each challenge is multiple-choice
      and always teaches on a wrong answer (never just "Wrong.").
WHERE: app/models/challenge.py

DESIGN NOTE (assumption, documented per project working rules): the spec
lists "questions" and "question_options" as a minimum table pair. We use
those two tables for the Before/After Assessment (Part H) and use this
separate Challenge / ChallengeOption pair for the gamified training levels
(Part A), since they serve different purposes (a challenge carries a
scenario, hint, and lesson; an assessment question is a plain quiz item).
This is more normalized than cramming both use cases into one table.
"""

from app.extensions import db

DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)

    scenario_type = db.Column(db.String(30), nullable=False)  # email, sms, url, password, mixed
    prompt = db.Column(db.Text, nullable=False)  # the email/SMS/URL/password shown to the player
    question_text = db.Column(db.Text, nullable=False)  # e.g. "Is this email safe?"

    difficulty = db.Column(db.String(10), default=DIFFICULTY_EASY, nullable=False)
    points_value = db.Column(db.Integer, default=100, nullable=False)
    time_limit_seconds = db.Column(db.Integer, default=60, nullable=False)

    hint_text = db.Column(db.Text, nullable=True)

    # Teaching content shown after ANY answer (never just "Wrong.")
    correct_explanation = db.Column(db.Text, nullable=False)
    warning_signs = db.Column(db.Text, nullable=False)   # newline-separated bullet points
    recommended_action = db.Column(db.Text, nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    level = db.relationship("Level", back_populates="challenges")
    options = db.relationship(
        "ChallengeOption", back_populates="challenge", order_by="ChallengeOption.order_index",
        cascade="all, delete-orphan",
    )
    attempts = db.relationship("Attempt", back_populates="challenge")

    def correct_option(self):
        return next((o for o in self.options if o.is_correct), None)

    def __repr__(self):
        return f"<Challenge {self.id} level={self.level_id}>"


class ChallengeOption(db.Model):
    __tablename__ = "challenge_options"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    challenge = db.relationship("Challenge", back_populates="options")

    def __repr__(self):
        return f"<ChallengeOption {self.id} correct={self.is_correct}>"
