"""
check.py
--------
WHAT: Routes for Part B (Message Analyzer) and Part C (URL Safety Checker).
WHY:  Both are open to logged-out visitors too — detection help shouldn't
      require an account — but if the user IS logged in, we log a
      privacy-safe usage record (risk level + indicator count + short
      preview only, never the raw text) for their dashboard/report and for
      admin analytics.
WHERE: app/routes/check.py, mounted at /check
SECURITY: message/URL text is never sent to any external API and never
      logged in full — see app/models/analyzer_history.py.
"""

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.extensions import db
from app.models.analyzer_history import ANALYZER_MESSAGE, ANALYZER_URL, AnalyzerHistory, make_safe_preview
from app.services.message_analyzer import analyze_message
from app.services.url_checker import analyze_url

check_bp = Blueprint("check", __name__, url_prefix="/check")


@check_bp.route("/message", methods=["GET", "POST"])
def message_analyzer():
    result = None
    submitted_text = ""
    if request.method == "POST":
        submitted_text = request.form.get("message_text", "")
        result = analyze_message(submitted_text)
        _log_usage(ANALYZER_MESSAGE, result.risk_level, len(result.indicators), submitted_text)

    return render_template("check/message_analyzer.html", result=result, submitted_text=submitted_text)


@check_bp.route("/url", methods=["GET", "POST"])
def url_checker():
    result = None
    submitted_url = ""
    if request.method == "POST":
        submitted_url = request.form.get("url_text", "")
        result = analyze_url(submitted_url)
        _log_usage(ANALYZER_URL, result.risk_level, len(result.indicators), submitted_url)

    return render_template("check/url_checker.html", result=result, submitted_url=submitted_url)


def _log_usage(analyzer_type: str, risk_level: str, indicator_count: int, raw_text: str):
    entry = AnalyzerHistory(
        user_id=current_user.id if current_user.is_authenticated else None,
        analyzer_type=analyzer_type,
        risk_level=risk_level,
        indicator_count=indicator_count,
        preview=make_safe_preview(raw_text),
    )
    db.session.add(entry)
    db.session.commit()
