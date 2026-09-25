"""
incident_wizard.py
-------------------
WHAT: The step logic for Part E, "I THINK I'VE BEEN SCAMMED". Maps the
      user's Step 1 selection to situation-specific guidance (reusing
      help_content.py where the scenario overlaps) and an urgency tier.
WHERE: app/services/incident_wizard.py — pure Python, no Flask/DB, so the
       classification logic is directly unit-testable.
"""

from dataclasses import dataclass, field
from typing import Optional

URGENCY_LOW = "LOW"
URGENCY_MODERATE = "MODERATE"
URGENCY_URGENT = "URGENT"

# what_happened option -> (matching help_content scenario key or None, urgency)
_STEP1_OPTIONS = {
    "suspicious_message": ("suspicious-message", URGENCY_LOW),
    "clicked_link": ("clicked-link", URGENCY_MODERATE),
    "shared_credentials": ("entered-credentials", URGENCY_MODERATE),
    "shared_otp": ("shared-otp", URGENCY_URGENT),
    "money_transferred": ("lost-money", URGENCY_URGENT),
    "account_compromised": ("account-compromised", URGENCY_MODERATE),
    "fake_job_offer": ("fake-job-offer", URGENCY_MODERATE),
    "impersonation": ("impersonation", URGENCY_LOW),
    "malware_concern": (None, URGENCY_MODERATE),
    "other": (None, URGENCY_LOW),
}

STEP1_LABELS = {
    "suspicious_message": "Suspicious message",
    "clicked_link": "Clicked a suspicious link",
    "shared_credentials": "Shared credentials",
    "shared_otp": "Shared an OTP",
    "money_transferred": "Money was transferred",
    "account_compromised": "Account compromised",
    "fake_job_offer": "Fake job offer",
    "impersonation": "Impersonation",
    "malware_concern": "Malware concern",
    "other": "Other",
}

_EVIDENCE_CHECKLIST_COMMON = [
    "Screenshots of the message/website/call log",
    "Exact date and time it happened",
    "Any phone numbers, email addresses, or URLs involved",
]
_EVIDENCE_CHECKLIST_FINANCIAL = [
    "Transaction ID / UTR number",
    "Amount and time of the transaction",
    "Bank/payment app used",
]


@dataclass
class WizardResult:
    urgency: str
    scenario_key: Optional[str]
    evidence_checklist: list = field(default_factory=list)
    show_financial_fraud_banner: bool = False


def classify(what_happened: str) -> WizardResult:
    scenario_key, urgency = _STEP1_OPTIONS.get(what_happened, (None, URGENCY_LOW))

    evidence = list(_EVIDENCE_CHECKLIST_COMMON)
    is_financial = what_happened in ("money_transferred", "shared_otp")
    if is_financial:
        evidence += _EVIDENCE_CHECKLIST_FINANCIAL

    return WizardResult(
        urgency=urgency,
        scenario_key=scenario_key,
        evidence_checklist=evidence,
        show_financial_fraud_banner=is_financial,
    )
