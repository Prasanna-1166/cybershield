"""
assessment_service.py
----------------------
WHAT: Scores a submitted Before/After Assessment (Part H) server-side and
      stores the result. Client submits answers; server looks up the
      correct options and grades — client-submitted "my score" is never
      trusted, same principle as the game.
WHERE: app/services/assessment_service.py
"""

from app.extensions import db
from app.models.assessment_attempt import AssessmentAttempt
from app.models.question import Question
from app.services.scoring import compute_improvement_percent


def submit_assessment(user_id: int, phase: str, answers: dict) -> AssessmentAttempt:
    """
    answers: {question_id (int): selected_option_id (int)}
    """
    questions = Question.query.filter_by(is_active=True).all()
    total = len(questions)
    correct = 0

    for question in questions:
        selected_option_id = answers.get(question.id)
        correct_option = question.correct_option()
        if correct_option and selected_option_id == correct_option.id:
            correct += 1

    score_percent = round((correct / total) * 100, 1) if total else 0.0

    attempt = AssessmentAttempt(
        user_id=user_id,
        phase=phase,
        total_questions=total,
        correct_answers=correct,
        score_percent=score_percent,
    )
    db.session.add(attempt)
    db.session.commit()
    return attempt


def get_improvement(user_id: int):
    """Returns (before_percent, after_percent, improvement_percent) or None
    values if either attempt is missing."""
    before = (
        AssessmentAttempt.query.filter_by(user_id=user_id, phase="before")
        .order_by(AssessmentAttempt.created_at.asc()).first()
    )
    after = (
        AssessmentAttempt.query.filter_by(user_id=user_id, phase="after")
        .order_by(AssessmentAttempt.created_at.desc()).first()
    )
    if not before or not after:
        return before, after, None
    improvement = compute_improvement_percent(before.score_percent, after.score_percent)
    return before, after, improvement
