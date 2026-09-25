"""
badge.py
--------
WHAT: The 8 badge definitions + the join table recording who earned what.
WHERE: app/models/badge.py
"""

from datetime import datetime, timezone

from app.extensions import db


class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(10), nullable=False)  # emoji, keeps Phase 1-6 dependency-free

    def __repr__(self):
        return f"<Badge {self.key}>"


class UserBadge(db.Model):
    __tablename__ = "user_badges"
    __table_args__ = (db.UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    awarded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User")
    badge = db.relationship("Badge")

    def __repr__(self):
        return f"<UserBadge user={self.user_id} badge={self.badge_id}>"
