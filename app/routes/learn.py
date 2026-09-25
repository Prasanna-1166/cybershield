"""
learn.py
--------
WHAT: Routes for Part G, the Cyber Safety Learning Center — short
      What/Warning-signs/Example/What-to-do cards.
WHERE: app/routes/learn.py, mounted at /learn
"""

from flask import Blueprint, abort, render_template, session

from app.models.learning_content import LearningContent

learn_bp = Blueprint("learn", __name__, url_prefix="/learn")


@learn_bp.route("/")
def index():
    lessons = LearningContent.query.filter_by(is_active=True).order_by(
        LearningContent.order_index
    ).all()
    viewed = set(session.get("viewed_lessons", []))
    return render_template("learn/index.html", lessons=lessons, viewed=viewed)


@learn_bp.route("/<key>")
def lesson(key):
    lessons = LearningContent.query.filter_by(is_active=True).order_by(
        LearningContent.order_index
    ).all()
    item = next((l for l in lessons if l.key == key), None)
    if item is None:
        abort(404)

    # Track distinct lessons viewed in-session for the "Cyber Learner" badge
    # (see badge_service.py — no dedicated DB table for lesson views in the
    # minimum schema, so we keep a lightweight session-based set). Also
    # doubles as the "lessons viewed" progress shown in the Learning Center.
    viewed = set(session.get("viewed_lessons", []))
    viewed.add(item.key)
    session["viewed_lessons"] = list(viewed)

    index_in_list = lessons.index(item)
    next_lesson = lessons[index_in_list + 1] if index_in_list + 1 < len(lessons) else None

    return render_template(
        "learn/lesson.html",
        item=item,
        next_lesson=next_lesson,
        viewed_count=len(viewed),
        total_lessons=len(lessons),
    )
