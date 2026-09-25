"""
test_incident_wizard.py
------------------------
Pure unit tests for app/services/incident_wizard.py.
Run with: python -m unittest tests.test_incident_wizard -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.incident_wizard import URGENCY_LOW, URGENCY_MODERATE, URGENCY_URGENT, classify


class IncidentWizardTests(unittest.TestCase):
    def test_money_transferred_is_urgent(self):
        r = classify("money_transferred")
        self.assertEqual(r.urgency, URGENCY_URGENT)
        self.assertTrue(r.show_financial_fraud_banner)
        self.assertIn("Transaction ID / UTR number", r.evidence_checklist)

    def test_shared_otp_is_urgent(self):
        r = classify("shared_otp")
        self.assertEqual(r.urgency, URGENCY_URGENT)

    def test_suspicious_message_is_low(self):
        r = classify("suspicious_message")
        self.assertEqual(r.urgency, URGENCY_LOW)
        self.assertFalse(r.show_financial_fraud_banner)

    def test_clicked_link_is_moderate(self):
        r = classify("clicked_link")
        self.assertEqual(r.urgency, URGENCY_MODERATE)

    def test_unknown_option_defaults_safely(self):
        r = classify("nonsense_key")
        self.assertEqual(r.urgency, URGENCY_LOW)
        self.assertIsNone(r.scenario_key)

    def test_non_financial_scenarios_exclude_financial_checklist(self):
        r = classify("clicked_link")
        self.assertNotIn("Transaction ID / UTR number", r.evidence_checklist)


if __name__ == "__main__":
    unittest.main()
