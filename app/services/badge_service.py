"""
badge_service.py
-----------------
WHAT: Builds the plain stats dict from the database and calls the pure
      app/services/badge_rules.py to figure out what's newly earned, then
      persists any new UserBadge rows.
WHERE: app/services/badge_service.py
"""

from app.extensions import db
from app.models.attempt import Attempt
from app.models.badge import Badge, UserBadge
from app.models.level import Level
from app.models.score import Score
from app.services.badge_rules import evaluate_badges
from app.services.scoring import compute_accuracy_percent


def _build_stats(user_id: int) -> dict:
    score = Score.query.filter_by(user_id=user_id).first()
    levels_completed = score.levels_completed if score else 0

    level_accuracy = {}
    for level in Level.query.all():
        attempts = Attempt.query.filter_by(user_id=user_id, level_id=level.id).all()
        if not attempts:
            continue
        correct = sum(1 for a in attempts if a.is_correct)
        wrong = sum(1 for a in attempts if not a.is_correct)
        level_accuracy[level.number] = compute_accuracy_percent(correct, wrong)

    fast_correct_count = Attempt.query.filter_by(
        user_id=user_id, is_correct=True
    ).filter(Attempt.response_time_seconds <= 10.0).count()

    # distinct_lessons_viewed is tracked client/route-side in Phase 3
    # (no dedicated "lesson view" table was in the minimum schema); routes
    # pass it in explicitly when available. Defaults to 0 here.
    return {
        "levels_completed": levels_completed,
        "level_accuracy": level_accuracy,
        "fast_correct_count": fast_correct_count,
    }


def evaluate_and_award(user_id: int, distinct_lessons_viewed: int = None) -> list:
    stats = _build_stats(user_id)
    if distinct_lessons_viewed is not None:
        stats["distinct_lessons_viewed"] = distinct_lessons_viewed

    already_earned_keys = {
        ub.badge.key for ub in UserBadge.query.filter_by(user_id=user_id).all()
    }

    newly_earned_keys = evaluate_badges(stats, already_earned_keys)
    if not newly_earned_keys:
        return []

    newly_earned_badges = []
    for key in newly_earned_keys:
        badge = Badge.query.filter_by(key=key).first()
        if badge is None:
            continue  # not seeded yet — skip gracefully rather than crash
        db.session.add(UserBadge(user_id=user_id, badge_id=badge.id))
        newly_earned_badges.append(badge)

    db.session.commit()
    return newly_earned_badges
