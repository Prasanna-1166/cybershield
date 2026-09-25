"""
attempt.py
----------
WHAT: One record per answer a user submits to a Challenge.
WHY:  This is the audit trail scoring is computed FROM — the client never
      gets to just say "I scored 500 points". The server recomputes
      correctness and points every time (see app/services/game_service.py).
WHERE: app/models/attempt.py
"""

from datetime import datetime, timezone

from app.extensions import db


class Attempt(db.Model):
    __tablename__ = "attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=False)

    selected_option_id = db.Column(db.Integer, db.ForeignKey("challenge_options.id"), nullable=True)
    is_correct = db.Column(db.Boolean, nullable=False)
    used_hint = db.Column(db.Boolean, default=False, nullable=False)
    response_time_seconds = db.Column(db.Float, nullable=False)
    points_awarded = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User")
    challenge = db.relationship("Challenge", back_populates="attempts")
    level = db.relationship("Level")

    def __repr__(self):
        return f"<Attempt user={self.user_id} challenge={self.challenge_id} correct={self.is_correct}>"
