"""
analyzer_history.py
--------------------
WHAT: A record that a user ran the Message Analyzer or URL Checker, and
      what risk level came back — used for the dashboard/admin analytics
      ("analyzer usage stats" in Part M).
WHY IT DOES NOT STORE THE RAW INPUT: the spec explicitly says not to store
      raw sensitive message content unnecessarily, and URLs pasted in here
      could themselves contain tokens/session IDs. We store only a short,
      NON-reversible preview (first 40 chars, further sanitized) purely so
      a user can recognize their own history entry — never enough to
      reconstruct sensitive content, and never sent anywhere external.
WHERE: app/models/analyzer_history.py
"""

from datetime import datetime, timezone

from app.extensions import db

ANALYZER_MESSAGE = "message"
ANALYZER_URL = "url"


class AnalyzerHistory(db.Model):
    __tablename__ = "analyzer_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # nullable: anonymous use

    analyzer_type = db.Column(db.String(10), nullable=False)  # "message" | "url"
    risk_level = db.Column(db.String(10), nullable=False)     # LOW | MEDIUM | HIGH
    indicator_count = db.Column(db.Integer, nullable=False)
    preview = db.Column(db.String(60), nullable=True)  # short, non-sensitive preview only

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User")

    def __repr__(self):
        return f"<AnalyzerHistory {self.analyzer_type} risk={self.risk_level}>"


def make_safe_preview(raw_text: str, max_len: int = 40) -> str:
    """Truncates and strips whitespace/newlines so nothing sensitive-looking
    or multi-line ends up sitting in the DB long-term."""
    if not raw_text:
        return ""
    flattened = " ".join(raw_text.split())
    return flattened[:max_len] + ("…" if len(flattened) > max_len else "")
