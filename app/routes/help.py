"""
help.py
-------
WHAT: Routes for Part D (Cyber Help Center), Part E (Incident Response
      Wizard), and Part F (Official Resources).
WHERE: app/routes/help.py, mounted at /help
IMPORTANT: this app never files a report or imitates the government portal.
      Every "report" action is an outbound link the browser opens itself.
"""

from flask import Blueprint, abort, render_template, request

from app.services.help_content import SCENARIO_ORDER, SCENARIOS
from app.services.incident_wizard import STEP1_LABELS, classify

help_bp = Blueprint("help", __name__, url_prefix="/help")

OFFICIAL_PORTAL_URL = "https://www.cybercrime.gov.in/"
CYBER_FRAUD_HELPLINE = "1930"


@help_bp.route("/")
def index():
    scenarios = [(key, SCENARIOS[key]["title"]) for key in SCENARIO_ORDER]
    return render_template("help/index.html", scenarios=scenarios)


@help_bp.route("/scenario/<scenario_key>")
def scenario(scenario_key):
    data = SCENARIOS.get(scenario_key)
    if data is None:
        abort(404)
    return render_template(
        "help/scenario.html", data=data, scenario_key=scenario_key,
        portal_url=OFFICIAL_PORTAL_URL, helpline=CYBER_FRAUD_HELPLINE,
    )


@help_bp.route("/wizard", methods=["GET", "POST"])
def wizard():
    result = None
    scenario_data = None
    selected = None

    if request.method == "POST":
        selected = request.form.get("what_happened")
        if selected:
            result = classify(selected)
            if result.scenario_key:
                scenario_data = SCENARIOS.get(result.scenario_key)

    return render_template(
        "help/wizard.html",
        step1_options=STEP1_LABELS,
        selected=selected,
        result=result,
        scenario_data=scenario_data,
        portal_url=OFFICIAL_PORTAL_URL,
        helpline=CYBER_FRAUD_HELPLINE,
    )


@help_bp.route("/resources")
def resources():
    return render_template(
        "help/resources.html", portal_url=OFFICIAL_PORTAL_URL, helpline=CYBER_FRAUD_HELPLINE,
    )
