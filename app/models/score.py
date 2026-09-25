"""
score.py
--------
WHAT: One running aggregate row per user: total score, accuracy, streak,
      levels completed. Recomputed server-side from Attempts — never
      trusted from the client.
WHERE: app/models/score.py
"""

from datetime import datetime, timezone

from app.extensions import db


class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    total_score = db.Column(db.Integer, default=0, nullable=False)
    correct_count = db.Column(db.Integer, default=0, nullable=False)
    wrong_count = db.Column(db.Integer, default=0, nullable=False)
    current_streak = db.Column(db.Integer, default=0, nullable=False)
    best_streak = db.Column(db.Integer, default=0, nullable=False)
    hints_used = db.Column(db.Integer, default=0, nullable=False)
    levels_completed = db.Column(db.Integer, default=0, nullable=False)
    current_level_number = db.Column(db.Integer, default=1, nullable=False)

    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User")

    @property
    def accuracy_percent(self) -> float:
        total = self.correct_count + self.wrong_count
        if total == 0:
            return 0.0
        return round((self.correct_count / total) * 100, 1)

    def __repr__(self):
        return f"<Score user={self.user_id} total={self.total_score}>"
