"""
message_analyzer.py
--------------------
WHAT: A rule-based, fully-educational analyzer for suspicious messages
      (emails/SMS/chat text pasted in by the user).
WHY:  Part B of the spec. Deliberately NO external API calls (message
      content never leaves the server, let alone goes to a third party),
      NO claims of certainty, and always framed as heuristic indicators.
WHERE: app/services/message_analyzer.py — zero Flask/DB imports, so it's
       fully unit-testable (see tests/test_message_analyzer.py).

Output shape: see analyze_message() docstring.
"""

import re
from dataclasses import dataclass, field

DISCLAIMER = "This is an educational heuristic and not a definitive malicious-message detector."

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

# Each rule: (indicator_label, weight, compiled_regex)
_RULES = [
    ("Urgency / threat language", 1, re.compile(
        r"\b(urgent|immediately|act now|final notice|account (will be|has been) (suspended|locked|closed)|"
        r"within 24 hours|failure to comply|legal action|your account is at risk)\b", re.I)),
    ("Request for OTP / verification code", 3, re.compile(
        r"\b(otp|one[- ]time password|verification code|security code)\b", re.I)),
    ("Request for password or PIN", 3, re.compile(
        r"\b(enter your password|confirm your password|share your pin|reveal your pin|atm pin)\b", re.I)),
    ("Request for payment or fees", 3, re.compile(
        r"\b(pay a fee|processing fee|convenience fee|clearance fee|pay now to (release|unlock)|wire transfer|"
        r"gift card|western union|pay via upi)\b", re.I)),
    ("Suspicious link present", 1, re.compile(
        r"(https?://|www\.)\S+", re.I)),
    ("Prize / reward claim", 3, re.compile(
        r"\b(you('| ha)ve won|congratulations you|claim your (prize|reward)|lucky winner|lottery|cashback of)\b", re.I)),
    ("KYC / account-verification impersonation", 3, re.compile(
        r"\b(kyc|update your kyc|verify your (account|identity)|re-?activate your account|bank account (will be|has been) blocked)\b", re.I)),
    ("Request for personal information", 3, re.compile(
        r"\b(aadhaar|social security number|ssn|card number|cvv|date of birth and address|full name and address)\b", re.I)),
    ("Unusual / suspicious instructions", 2, re.compile(
        r"\b(do not tell anyone|keep this confidential|don'?t inform (the )?bank|delete this message after reading)\b", re.I)),
    ("Generic impersonal greeting", 1, re.compile(
        r"\b(dear (customer|user|valued customer|sir/madam))\b", re.I)),
]

_HIGH_WEIGHT_LABELS = {
    "Request for OTP / verification code",
    "Request for password or PIN",
    "KYC / account-verification impersonation",
}


@dataclass
class AnalyzerResult:
    risk_level: str
    score: int
    indicators: list = field(default_factory=list)  # list[str]
    explanation: str = ""
    recommended_action: str = ""
    disclaimer: str = DISCLAIMER


def analyze_message(message: str) -> AnalyzerResult:
    """
    Scans `message` against a fixed rule set and returns a risk assessment.
    Never mutates or stores `message` — pure function, caller decides what
    (if anything) to persist. Per spec, the caller should NOT persist raw
    message content — only the resulting risk level/indicators.
    """
    if not message or not message.strip():
        return AnalyzerResult(
            risk_level=RISK_LOW,
            score=0,
            indicators=[],
            explanation="No message text was provided to analyze.",
            recommended_action="Paste the suspicious message text above and try again.",
        )

    indicators = []
    score = 0
    high_weight_hits = 0

    for label, weight, pattern in _RULES:
        if pattern.search(message):
            indicators.append(label)
            score += weight
            if label in _HIGH_WEIGHT_LABELS:
                high_weight_hits += 1

    if score == 0:
        risk = RISK_LOW
    elif score <= 3 and high_weight_hits == 0:
        risk = RISK_LOW
    elif score <= 6 or high_weight_hits == 1:
        risk = RISK_MEDIUM
    else:
        risk = RISK_HIGH

    explanation = _build_explanation(risk, indicators)
    recommended_action = _build_recommendation(risk)

    return AnalyzerResult(
        risk_level=risk,
        score=score,
        indicators=indicators,
        explanation=explanation,
        recommended_action=recommended_action,
    )


def _build_explanation(risk: str, indicators: list) -> str:
    if not indicators:
        return "No indicators commonly associated with phishing or scam messages were detected in this text."
    joined = "; ".join(indicators)
    return (
        f"This message contains {len(indicators)} indicator(s) commonly associated with "
        f"phishing or scam messages: {joined}."
    )


def _build_recommendation(risk: str) -> str:
    if risk == RISK_HIGH:
        return (
            "Do not click any links, reply, or share any information. Verify independently by "
            "contacting the organization directly using a phone number or website you already "
            "trust (not one provided in this message). Consider reporting it."
        )
    if risk == RISK_MEDIUM:
        return (
            "Treat this message with caution. Avoid clicking links or sharing information until "
            "you've verified it independently through an official channel."
        )
    return (
        "No strong warning signs were detected, but always stay alert — verify anything asking "
        "for money, credentials, or personal information through an official channel."
    )
