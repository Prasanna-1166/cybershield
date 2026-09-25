"""
test_message_analyzer.py
-------------------------
Pure unit tests for app/services/message_analyzer.py — no Flask/DB needed.
All sample messages are fictional simulations (per the spec's safety
guardrails) — no real organizations, no real phone numbers/URLs.

Run with: python -m unittest tests.test_message_analyzer -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.message_analyzer import RISK_HIGH, RISK_LOW, RISK_MEDIUM, analyze_message


class MessageAnalyzerTests(unittest.TestCase):
    def test_empty_message(self):
        r = analyze_message("")
        self.assertEqual(r.risk_level, RISK_LOW)
        self.assertEqual(r.indicators, [])

    def test_benign_message_is_low_risk(self):
        r = analyze_message("Hi Raj, are we still meeting for lunch tomorrow at 1pm?")
        self.assertEqual(r.risk_level, RISK_LOW)

    def test_bare_link_alone_is_low_risk(self):
        r = analyze_message("Check out this article: https://example.com/article")
        self.assertEqual(r.risk_level, RISK_LOW)

    def test_single_otp_mention_is_medium(self):
        r = analyze_message("Your OTP for login is required to proceed.")
        self.assertEqual(r.risk_level, RISK_MEDIUM)
        self.assertIn("Request for OTP / verification code", r.indicators)

    def test_classic_kyc_phishing_scenario_is_high(self):
        # Fictional simulation — no real bank/organization named.
        text = (
            "Dear Customer, your bank account has been blocked due to KYC issues. "
            "Verify your account immediately by entering your password and OTP at "
            "http://example-scam-test.invalid within 24 hours or your account will be suspended."
        )
        r = analyze_message(text)
        self.assertEqual(r.risk_level, RISK_HIGH)
        self.assertIn("KYC / account-verification impersonation", r.indicators)
        self.assertIn("Request for OTP / verification code", r.indicators)

    def test_prize_plus_fee_plus_secrecy_is_high(self):
        text = (
            "Congratulations you have won a lottery of 5000 dollars! Claim your prize now by "
            "paying a small processing fee via gift card. Do not tell anyone about this offer."
        )
        r = analyze_message(text)
        self.assertEqual(r.risk_level, RISK_HIGH)

    def test_disclaimer_always_present(self):
        r = analyze_message("anything")
        self.assertIn("educational heuristic", r.disclaimer)

    def test_never_claims_certainty(self):
        text = "Dear Customer, share your PIN and OTP immediately to avoid account suspension."
        r = analyze_message(text)
        for phrase in ("definitely", "100% malicious", "guaranteed scam"):
            self.assertNotIn(phrase, r.explanation.lower())
            self.assertNotIn(phrase, r.recommended_action.lower())


if __name__ == "__main__":
    unittest.main()
