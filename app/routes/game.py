"""
game.py
-------
WHAT: Routes for the gamified training (Part A): pick a level, play through
      its challenges one at a time, submit an answer, see the teaching
      feedback. Scoring is entirely server-side (see game_service.py).
WHERE: app/routes/game.py, mounted at /play
"""

import time

from flask import Blueprint, abort, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.models.challenge import Challenge
from app.models.level import Level
from app.models.score import Score
from app.services import game_service

game_bp = Blueprint("game", __name__, url_prefix="/play")


@game_bp.route("/")
@login_required
def levels():
    levels = Level.query.filter_by(is_active=True).order_by(Level.order_index).all()
    score = game_service.get_or_create_score(current_user.id)
    return render_template("game/levels.html", levels=levels, score=score)


@game_bp.route("/level/<int:level_number>")
@login_required
def play_level(level_number):
    level = Level.query.filter_by(number=level_number, is_active=True).first()
    if level is None:
        abort(404)

    challenges = Challenge.query.filter_by(level_id=level.id, is_active=True).order_by(
        Challenge.order_index
    ).all()
    if not challenges:
        return render_template("game/no_challenges.html", level=level)

    # Track progress through this level's challenges using the session
    # (simple, no extra DB table needed for "where am I right now").
    session_key = f"level_{level.id}_index"
    index = session.get(session_key, 0)
    if index >= len(challenges):
        index = 0
        session[session_key] = 0

    challenge = challenges[index]
    session["current_challenge_started_at"] = time.time()

    return render_template(
        "game/play.html",
        level=level,
        challenge=challenge,
        challenge_number=index + 1,
        total_challenges=len(challenges),
    )


@game_bp.route("/answer/<int:challenge_id>", methods=["POST"])
@login_required
def answer(challenge_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if challenge is None:
        abort(404)

    selected_option_id = request.form.get("option_id", type=int)
    used_hint = request.form.get("used_hint") == "1"

    started_at = session.get("current_challenge_started_at")
    response_time = max(0.0, time.time() - started_at) if started_at else 9999.0

    result = game_service.submit_answer(
        user_id=current_user.id,
        challenge_id=challenge.id,
        selected_option_id=selected_option_id,
        used_hint=used_hint,
        response_time_seconds=response_time,
    )

    # Advance the in-session pointer for this level regardless of right/wrong
    # (per spec: every wrong answer teaches, then the player continues).
    session_key = f"level_{challenge.level_id}_index"
    session[session_key] = session.get(session_key, 0) + 1

    return render_template(
        "game/feedback.html",
        level=challenge.level,
        result=result,
    )


@game_bp.route("/hint/<int:challenge_id>")
@login_required
def hint(challenge_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if challenge is None:
        abort(404)
    return jsonify({"hint": challenge.hint_text or "No hint available for this challenge."})
