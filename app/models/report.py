"""
report.py
---------
WHAT: A stored snapshot of a user's Personalized Cyber Safety Report
      (Part I), saved as JSON so the report page can show history without
      recomputing everything, and so it survives if underlying attempts
      are later pruned.
WHERE: app/models/report.py
"""

import json
from datetime import datetime, timezone

from app.extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    data_json = db.Column(db.Text, nullable=False)  # serialized report dict, see report_service.py
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User")

    @property
    def data(self) -> dict:
        return json.loads(self.data_json)

    def __repr__(self):
        return f"<Report user={self.user_id} at={self.generated_at}>"
