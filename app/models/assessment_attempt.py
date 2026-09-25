"""
assessment_attempt.py
----------------------
WHAT: One row per Before/After Assessment a user takes (Part H).
WHERE: app/models/assessment_attempt.py
"""

from datetime import datetime, timezone

from app.extensions import db

PHASE_BEFORE = "before"
PHASE_AFTER = "after"


class AssessmentAttempt(db.Model):
    __tablename__ = "assessment_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    phase = db.Column(db.String(10), nullable=False)  # "before" | "after"

    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    score_percent = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User")

    def __repr__(self):
        return f"<AssessmentAttempt user={self.user_id} phase={self.phase} score={self.score_percent}>"
