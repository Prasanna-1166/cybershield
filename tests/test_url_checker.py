"""
test_url_checker.py
--------------------
Pure unit tests for app/services/url_checker.py — no Flask/DB/network needed.
Confirms the checker never raises on malformed input and classifies a
representative structural pattern correctly. Domains used are either
example/test reserved domains or fictional look-alikes — nothing real is
targeted or visited (this module never makes a network call at all).

Run with: python -m unittest tests.test_url_checker -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.url_checker import RISK_HIGH, RISK_LOW, RISK_MEDIUM, analyze_url


class UrlCheckerTests(unittest.TestCase):
    def test_empty_url(self):
        r = analyze_url("")
        self.assertEqual(r.risk_level, RISK_LOW)

    def test_clean_https_url_is_low_risk(self):
        r = analyze_url("https://www.example.com/about")
        self.assertEqual(r.risk_level, RISK_LOW)
        self.assertEqual(r.indicators, [])

    def test_raw_ip_address_is_flagged(self):
        r = analyze_url("http://192.168.10.55/login")
        self.assertIn("Uses a raw IP address instead of a domain name", r.indicators)
        self.assertIn(r.risk_level, (RISK_MEDIUM, RISK_HIGH))

    def test_known_shortener_is_flagged(self):
        r = analyze_url("https://bit.ly/3xample")
        self.assertTrue(any("shortening" in i for i in r.indicators))

    def test_lookalike_brand_domain_is_high_risk(self):
        r = analyze_url("http://paypa1-secure-login.com/verify")
        self.assertEqual(r.risk_level, RISK_HIGH)
        self.assertTrue(any("resembles 'paypal'" in i for i in r.indicators))

    def test_ip_with_unusual_port_and_executable_is_high_risk(self):
        r = analyze_url("http://203.0.113.5:8080/update.exe")
        self.assertEqual(r.risk_level, RISK_HIGH)

    def test_at_symbol_trick_is_flagged(self):
        r = analyze_url("http://google.com@malicious-test.example/path")
        self.assertTrue(any("real destination may be hidden" in i for i in r.indicators))

    def test_never_crashes_on_garbage_input(self):
        garbage_inputs = ["not a url at all", "://///", "http://", "a" * 500, "😀😀😀"]
        for g in garbage_inputs:
            try:
                analyze_url(g)
            except Exception as e:
                self.fail(f"analyze_url raised on input {g!r}: {e}")

    def test_disclaimer_always_present(self):
        r = analyze_url("https://example.com")
        self.assertIn("does not prove", r.disclaimer)


if __name__ == "__main__":
    unittest.main()
