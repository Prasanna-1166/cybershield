"""
report_service.py
------------------
WHAT: Builds the Personalized Cyber Safety Report (Part I) by pulling
      together Score, per-category Attempt accuracy, hints used, average
      response time, before/after assessment improvement, and simple
      strong/weak-area + recommended-lesson logic. Stores a JSON snapshot.
WHERE: app/services/report_service.py
"""

import json

from app.extensions import db
from app.models.attempt import Attempt
from app.models.level import Level
from app.models.report import Report
from app.models.score import Score
from app.services.assessment_service import get_improvement
from app.services.scoring import (
    classify_security_score,
    compute_accuracy_percent,
    compute_rank,
    compute_security_score,
    next_rank_progress,
)

# Maps a level's key to the Learning Center category recommended when the
# user is weak in that level — used to power "recommended lessons".
_LEVEL_KEY_TO_LESSON_CATEGORY = {
    "phishing_hunter": "phishing",
    "url_detective": "suspicious_urls",
    "account_guardian": "password_safety",
    "scam_spotter": "online_scams",
    "cyber_escape": "basic_incident_response",
}


def build_report(user_id: int) -> dict:
    score = Score.query.filter_by(user_id=user_id).first()

    per_level = []
    weak_categories = []
    strong_categories = []

    for level in Level.query.order_by(Level.order_index).all():
        attempts = Attempt.query.filter_by(user_id=user_id, level_id=level.id).all()
        correct = sum(1 for a in attempts if a.is_correct)
        wrong = sum(1 for a in attempts if not a.is_correct)
        accuracy = compute_accuracy_percent(correct, wrong)
        entry = {
            "level_number": level.number,
            "level_name": level.name,
            "attempts": len(attempts),
            "accuracy_percent": accuracy,
        }
        per_level.append(entry)

        if attempts:
            if accuracy < 70:
                weak_categories.append(level.name)
            elif accuracy >= 90:
                strong_categories.append(level.name)

    all_attempts = Attempt.query.filter_by(user_id=user_id).all()
    avg_response_time = (
        round(sum(a.response_time_seconds for a in all_attempts) / len(all_attempts), 1)
        if all_attempts else 0.0
    )

    before, after, improvement = get_improvement(user_id)

    total_levels = Level.query.count()
    security_score = compute_security_score(
        accuracy_percent=score.accuracy_percent if score else 0.0,
        levels_completed=score.levels_completed if score else 0,
        total_levels=total_levels,
        assessment_improvement=improvement,
    )

    recommended_lessons = []
    for level in Level.query.all():
        if level.name in weak_categories:
            category = _LEVEL_KEY_TO_LESSON_CATEGORY.get(level.key)
            if category:
                recommended_lessons.append(category)

    report_data = {
        "overall_score": score.total_score if score else 0,
        "overall_accuracy_percent": score.accuracy_percent if score else 0.0,
        "levels_completed": score.levels_completed if score else 0,
        "hints_used": score.hints_used if score else 0,
        "avg_response_time_seconds": avg_response_time,
        "per_level_performance": per_level,
        "strong_areas": strong_categories,
        "weak_areas": weak_categories,
        "recommended_lesson_categories": recommended_lessons,
        "before_assessment_percent": before.score_percent if before else None,
        "after_assessment_percent": after.score_percent if after else None,
        "improvement_percent": improvement,
        "security_score": security_score,
        "security_score_classification": classify_security_score(security_score),
        "rank": compute_rank(score.total_score if score else 0),
        "rank_progress": next_rank_progress(score.total_score if score else 0),
        "total_levels": total_levels,
    }
    return report_data


def save_report(user_id: int) -> Report:
    data = build_report(user_id)
    report = Report(user_id=user_id, data_json=json.dumps(data))
    db.session.add(report)
    db.session.commit()
    return report
