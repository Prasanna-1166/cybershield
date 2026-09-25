"""
game_service.py
----------------
WHAT: The DB-facing half of the training game. Records an Attempt,
      recomputes the user's Score from server-side truth (never trusts a
      client-submitted "I got it right" or "my score is X"), and checks for
      level completion + badge eligibility.
WHERE: app/services/game_service.py
HOW IT'S TESTED: the scoring math itself lives in scoring.py and is unit
      tested directly (tests/test_scoring.py). This file is exercised via
      Flask route tests once the full stack is installed (Phase 2 route
      tests, tests/test_game.py).
"""

from app.extensions import db
from app.models.attempt import Attempt
from app.models.challenge import Challenge
from app.models.score import Score
from app.services import badge_service
from app.services.scoring import level_completion_bonus, score_attempt


def get_or_create_score(user_id: int) -> Score:
    score = Score.query.filter_by(user_id=user_id).first()
    if score is None:
        score = Score(user_id=user_id)
        db.session.add(score)
        db.session.commit()
    return score


def submit_answer(user_id: int, challenge_id: int, selected_option_id: int,
                   used_hint: bool, response_time_seconds: float) -> dict:
    """
    Validates and records one answer. Returns a dict the route can render:
        {
          "is_correct": bool, "points_awarded": int, "correct_option_id": int,
          "correct_explanation": str, "warning_signs": str, "recommended_action": str,
          "level_completed": bool, "newly_earned_badges": [Badge, ...],
        }
    """
    challenge = db.session.get(Challenge, challenge_id)
    if challenge is None:
        raise ValueError(f"Challenge {challenge_id} not found")

    correct_option = challenge.correct_option()
    is_correct = bool(correct_option and correct_option.id == selected_option_id)

    result = score_attempt(is_correct, used_hint, response_time_seconds)

    attempt = Attempt(
        user_id=user_id,
        challenge_id=challenge.id,
        level_id=challenge.level_id,
        selected_option_id=selected_option_id,
        is_correct=is_correct,
        used_hint=used_hint,
        response_time_seconds=response_time_seconds,
        points_awarded=result.points_awarded,
    )
    db.session.add(attempt)

    score = get_or_create_score(user_id)
    score.total_score += result.points_awarded
    if is_correct:
        score.correct_count += 1
        score.current_streak += 1
        score.best_streak = max(score.best_streak, score.current_streak)
    else:
        score.wrong_count += 1
        score.current_streak = 0
    if used_hint:
        score.hints_used += 1

    level_completed = _check_and_apply_level_completion(user_id, challenge.level_id, score)

    db.session.commit()

    newly_earned_badges = badge_service.evaluate_and_award(user_id)

    return {
        "is_correct": is_correct,
        "points_awarded": result.points_awarded,
        "fast_bonus_applied": result.fast_bonus_applied,
        "hint_penalty_applied": result.hint_penalty_applied,
        "correct_option_id": correct_option.id if correct_option else None,
        "correct_explanation": challenge.correct_explanation,
        "warning_signs": challenge.warning_signs,
        "recommended_action": challenge.recommended_action,
        "level_completed": level_completed,
        "newly_earned_badges": newly_earned_badges,
    }


def _check_and_apply_level_completion(user_id: int, level_id: int, score: Score) -> bool:
    """
    A level counts as 'completed' the first time the user has answered every
    active challenge in it CORRECTLY at least once. Awards the one-time
    +200 completion bonus. Idempotent: won't double-award on replay.
    """
    level_challenges = Challenge.query.filter_by(level_id=level_id, is_active=True).all()
    if not level_challenges:
        return False

    challenge_ids = [c.id for c in level_challenges]
    correctly_answered_ids = {
        a.challenge_id for a in Attempt.query.filter(
            Attempt.user_id == user_id,
            Attempt.challenge_id.in_(challenge_ids),
            Attempt.is_correct.is_(True),
        ).all()
    }

    just_completed_now = set(challenge_ids).issubset(correctly_answered_ids)
    if not just_completed_now:
        return False

    # Idempotency check: was this level already marked completed before
    # this attempt? We approximate "already completed" by checking whether
    # every challenge had a correct attempt BEFORE the one just inserted
    # (i.e. more than one correct attempt exists in total for the set, or
    # simpler: track via score.levels_completed vs level order). To keep
    # this simple and correct for Phase 2, we use a marker table-free
    # approach: only award once by checking current_level_number.
    from app.models.level import Level
    level = db.session.get(Level, level_id)
    if level and level.number == score.current_level_number:
        score.total_score += level_completion_bonus()
        score.levels_completed += 1
        score.current_level_number += 1
        return True

    return False
