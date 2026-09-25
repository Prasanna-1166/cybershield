"""
test_badges.py
--------------
Pure unit tests for app/services/badge_rules.py — no Flask/DB needed.
Run with: python -m unittest tests.test_badges -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.badge_rules import evaluate_badges


class BadgeRuleTests(unittest.TestCase):
    def test_no_badges_from_empty_stats(self):
        self.assertEqual(evaluate_badges({}, set()), set())

    def test_perfect_level1_gives_phishing_hunter(self):
        r = evaluate_badges({"level_accuracy": {1: 100.0}}, set())
        self.assertIn("phishing_hunter", r)
        self.assertNotIn("url_detective", r)

    def test_imperfect_level_gives_nothing(self):
        r = evaluate_badges({"level_accuracy": {1: 90.0}}, set())
        self.assertEqual(r, set())

    def test_already_earned_not_reawarded(self):
        r = evaluate_badges({"level_accuracy": {1: 100.0}}, {"phishing_hunter"})
        self.assertNotIn("phishing_hunter", r)

    def test_fast_thinker(self):
        self.assertIn("fast_thinker", evaluate_badges({"fast_correct_count": 5}, set()))
        self.assertNotIn("fast_thinker", evaluate_badges({"fast_correct_count": 4}, set()))

    def test_cyber_learner(self):
        r = evaluate_badges({"distinct_lessons_viewed": 5}, set())
        self.assertIn("cyber_learner", r)

    def test_security_expert_needs_all_5_levels(self):
        self.assertIn("security_expert", evaluate_badges({"levels_completed": 5}, set()))
        self.assertNotIn("security_expert", evaluate_badges({"levels_completed": 4}, set()))

    def test_champion_awarded_when_last_badge_completes_the_set(self):
        already = {
            "phishing_hunter", "url_detective", "password_protector",
            "scam_spotter", "fast_thinker", "cyber_learner",
        }
        r = evaluate_badges({"levels_completed": 5}, already)
        self.assertIn("security_expert", r)
        self.assertIn("cybershield_champion", r)

    def test_champion_not_awarded_if_incomplete(self):
        already = {"phishing_hunter", "url_detective"}
        r = evaluate_badges({"levels_completed": 5}, already)
        self.assertIn("security_expert", r)
        self.assertNotIn("cybershield_champion", r)


if __name__ == "__main__":
    unittest.main()
