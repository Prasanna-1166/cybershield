"""
Makes every model importable as `from app.models import User, Role, ...`
and ensures every model class is registered with SQLAlchemy's metadata
before db.create_all() runs. Import order matters for foreign keys.
"""

from app.models.role import Role
from app.models.user import User
from app.models.level import Level
from app.models.challenge import Challenge, ChallengeOption
from app.models.attempt import Attempt
from app.models.score import Score
from app.models.badge import Badge, UserBadge
from app.models.learning_content import LearningContent
from app.models.question import Question, QuestionOption
from app.models.assessment_attempt import AssessmentAttempt
from app.models.report import Report
from app.models.analyzer_history import AnalyzerHistory

__all__ = [
    "Role", "User", "Level", "Challenge", "ChallengeOption", "Attempt",
    "Score", "Badge", "UserBadge", "LearningContent", "Question",
    "QuestionOption", "AssessmentAttempt", "Report", "AnalyzerHistory",
]
