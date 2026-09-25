"""
main.py
-------
WHAT: Home/about (public), plus the authenticated Dashboard (Part J),
      Leaderboard (Part K), Profile, Before/After Assessment (Part H), and
      Personalized Cyber Safety Report (Part I).
WHERE: app/routes/main.py, mounted at /
"""

from flask import Blueprint, flash, render_template, request, session
from flask_login import current_user, login_required

from app.extensions import db
from app.models.assessment_attempt import PHASE_AFTER, PHASE_BEFORE
from app.models.badge import Badge, UserBadge
from app.models.challenge import Challenge
from app.models.learning_content import LearningContent
from app.models.level import Level
from app.models.question import Question
from app.models.score import Score
from app.services import badge_service, report_service
from app.services.assessment_service import get_improvement, submit_assessment
from app.services.scoring import compute_accuracy_percent

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    # Real, current counts from the database — never hard-coded/fabricated
    # marketing numbers (see the landing-page "By the numbers" section).
    stats = {
        "levels": Level.query.count(),
        "challenges": Challenge.query.count(),
        "lessons": LearningContent.query.filter_by(is_active=True).count(),
        "badges": Badge.query.count(),
    }
    return render_template("home.html", stats=stats)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    score = Score.query.filter_by(user_id=current_user.id).first()

    # Opportunistically check badge eligibility whenever the dashboard loads
    # (covers the "Cyber Learner" badge, which depends on session-tracked
    # lesson views rather than a DB-recorded event).
    viewed_lessons = session.get("viewed_lessons", [])
    newly_earned = badge_service.evaluate_and_award(
        current_user.id, distinct_lessons_viewed=len(viewed_lessons)
    )

    earned_badges = [ub.badge for ub in UserBadge.query.filter_by(user_id=current_user.id).all()]
    levels = Level.query.order_by(Level.order_index).all()

    before, after, improvement = get_improvement(current_user.id)
    report_data = report_service.build_report(current_user.id)

    all_badges = Badge.query.order_by(Badge.id).all()
    earned_badge_ids = {b.id for b in earned_badges}

    return render_template(
        "dashboard/dashboard.html",
        score=score,
        levels=levels,
        earned_badges=earned_badges,
        all_badges=all_badges,
        earned_badge_ids=earned_badge_ids,
        newly_earned=newly_earned,
        before=before,
        after=after,
        improvement=improvement,
        report=report_data,
    )


@main_bp.route("/leaderboard")
def leaderboard():
    # No email addresses shown — only display name/username, score, accuracy.
    top_scores = Score.query.order_by(Score.total_score.desc()).limit(50).all()
    total_levels = Level.query.count()
    rows = []
    for rank, score in enumerate(top_scores, start=1):
        rows.append({
            "rank": rank,
            "user_id": score.user_id,
            "display_name": score.user.display(),
            "total_score": score.total_score,
            "accuracy": score.accuracy_percent,
            "levels_completed": score.levels_completed,
        })
    return render_template("dashboard/leaderboard.html", rows=rows, total_levels=total_levels)


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        new_display_name = request.form.get("display_name", "").strip()
        if new_display_name:
            current_user.display_name = new_display_name[:50]
            db.session.commit()
            flash("Profile updated.", "success")
    return render_template("dashboard/profile.html", user=current_user)


@main_bp.route("/assessment/<phase>", methods=["GET", "POST"])
@login_required
def assessment(phase):
    if phase not in (PHASE_BEFORE, PHASE_AFTER):
        phase = PHASE_BEFORE

    if request.method == "POST":
        answers = {}
        for key, value in request.form.items():
            if key.startswith("q_"):
                try:
                    question_id = int(key.split("_", 1)[1])
                    answers[question_id] = int(value)
                except ValueError:
                    continue
        attempt = submit_assessment(current_user.id, phase, answers)
        flash("Assessment submitted.", "success")
        return render_template("dashboard/assessment_result.html", attempt=attempt, phase=phase)

    questions = Question.query.filter_by(is_active=True).all()
    return render_template("dashboard/assessment.html", questions=questions, phase=phase)


@main_bp.route("/report")
@login_required
def report():
    data = report_service.build_report(current_user.id)
    return render_template("dashboard/report.html", data=data)


@main_bp.route("/report/pdf")
@login_required
def report_pdf():
    from flask import Response

    from app.services.pdf_report import build_report_pdf

    data = report_service.build_report(current_user.id)
    pdf_bytes = build_report_pdf(current_user.display(), data)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=cybershield-report.pdf"},
    )
