"""
admin.py
--------
WHAT: Part M — the Admin Dashboard. Every route here requires ADMIN role
      (see app/routes/decorators.py::admin_required).
WHERE: app/routes/admin.py, mounted at /admin

Scope note: full drag-and-drop content editors are beyond a college-project
Phase 6 — CRUD here uses simple forms (create/edit/delete), which is what
"real backend badge/content logic, not decorative" requires without
building a second frontend framework.
"""

from datetime import datetime, timedelta, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models.analyzer_history import AnalyzerHistory
from app.models.attempt import Attempt
from app.models.challenge import Challenge
from app.models.learning_content import LearningContent
from app.models.level import Level
from app.models.question import Question
from app.models.user import User
from app.routes.decorators import admin_required
from app.services.scoring import compute_accuracy_percent

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

_RANGE_LABELS = {
    "today": "Today",
    "7d": "Last 7 days",
    "30d": "Last 30 days",
    "all": "All time",
}


def _range_cutoff(range_key: str):
    now = datetime.now(timezone.utc)
    if range_key == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if range_key == "7d":
        return now - timedelta(days=7)
    if range_key == "30d":
        return now - timedelta(days=30)
    return None  # "all"


# ----------------------------------------------------------------------
# Dashboard / analytics
# ----------------------------------------------------------------------
@admin_bp.route("/")
@admin_required
def dashboard():
    range_key = request.args.get("range", "all")
    if range_key not in _RANGE_LABELS:
        range_key = "all"
    cutoff = _range_cutoff(range_key)

    total_users = User.query.count()

    attempt_query = Attempt.query
    analyzer_query = AnalyzerHistory.query
    if cutoff is not None:
        attempt_query = attempt_query.filter(Attempt.created_at >= cutoff)
        analyzer_query = analyzer_query.filter(AnalyzerHistory.created_at >= cutoff)

    total_attempts = attempt_query.count()
    correct_attempts = attempt_query.filter_by(is_correct=True).count()
    overall_accuracy = compute_accuracy_percent(correct_attempts, total_attempts - correct_attempts)

    analyzer_counts = {
        "message": analyzer_query.filter_by(analyzer_type="message").count(),
        "url": analyzer_query.filter_by(analyzer_type="url").count(),
    }
    risk_breakdown = {
        level: analyzer_query.filter_by(risk_level=level).count()
        for level in ("LOW", "MEDIUM", "HIGH")
    }

    # Hardest challenges: lowest correct-rate among challenges with >=1 attempt
    # (always all-time — a meaningful "hardest challenge" needs a real sample).
    challenge_stats = []
    for challenge in Challenge.query.filter_by(is_active=True).all():
        c_attempts = [a for a in challenge.attempts]
        if not c_attempts:
            continue
        correct = sum(1 for a in c_attempts if a.is_correct)
        accuracy = compute_accuracy_percent(correct, len(c_attempts) - correct)
        challenge_stats.append({
            "challenge": challenge, "attempts": len(c_attempts), "accuracy": accuracy,
        })
    hardest_challenges = sorted(challenge_stats, key=lambda x: x["accuracy"])[:5]

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_attempts=total_attempts,
        overall_accuracy=overall_accuracy,
        analyzer_counts=analyzer_counts,
        risk_breakdown=risk_breakdown,
        hardest_challenges=hardest_challenges,
        range_key=range_key,
        range_labels=_RANGE_LABELS,
    )


# ----------------------------------------------------------------------
# Users
# ----------------------------------------------------------------------
@admin_bp.route("/users")
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_user_active(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    user.is_active_account = not user.is_active_account
    db.session.commit()
    flash(f"{user.username} is now {'active' if user.is_active_account else 'deactivated'}.", "info")
    return redirect(url_for("admin.users"))


# ----------------------------------------------------------------------
# Levels & Challenges (read + toggle-active; full authoring via seed data)
# ----------------------------------------------------------------------
@admin_bp.route("/levels")
@admin_required
def levels():
    all_levels = Level.query.order_by(Level.order_index).all()
    return render_template("admin/levels.html", levels=all_levels)


@admin_bp.route("/levels/<int:level_id>/challenges")
@admin_required
def challenges(level_id):
    level = Level.query.filter_by(id=level_id).first_or_404()
    return render_template("admin/challenges.html", level=level)


@admin_bp.route("/challenges/<int:challenge_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_challenge_active(challenge_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if challenge is None:
        flash("Challenge not found.", "danger")
        return redirect(url_for("admin.levels"))
    challenge.is_active = not challenge.is_active
    db.session.commit()
    flash("Challenge status updated.", "info")
    return redirect(url_for("admin.challenges", level_id=challenge.level_id))


# ----------------------------------------------------------------------
# Learning content CRUD (active/inactive)
# ----------------------------------------------------------------------
@admin_bp.route("/learning-content")
@admin_required
def learning_content():
    items = LearningContent.query.order_by(LearningContent.order_index).all()
    return render_template("admin/learning_content.html", items=items)


@admin_bp.route("/learning-content/<int:item_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_learning_content_active(item_id):
    item = LearningContent.query.filter_by(id=item_id).first()
    if item is None:
        flash("Lesson not found.", "danger")
        return redirect(url_for("admin.learning_content"))
    item.is_active = not item.is_active
    db.session.commit()
    flash("Lesson status updated.", "info")
    return redirect(url_for("admin.learning_content"))


# ----------------------------------------------------------------------
# Assessment questions
# ----------------------------------------------------------------------
@admin_bp.route("/questions")
@admin_required
def questions():
    all_questions = Question.query.order_by(Question.category).all()
    return render_template("admin/questions.html", questions=all_questions)


@admin_bp.route("/questions/<int:question_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_question_active(question_id):
    question = Question.query.filter_by(id=question_id).first()
    if question is None:
        flash("Question not found.", "danger")
        return redirect(url_for("admin.questions"))
    question.is_active = not question.is_active
    db.session.commit()
    flash("Question status updated.", "info")
    return redirect(url_for("admin.questions"))
