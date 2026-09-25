"""
test_scoring.py
----------------
Pure unit tests for app/services/scoring.py — no Flask/DB needed.
Run with: python -m unittest tests.test_scoring -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.scoring import (
    classify_security_score,
    compute_accuracy_percent,
    compute_improvement_percent,
    compute_rank,
    compute_security_score,
    next_rank_progress,
    score_attempt,
)


class ScoringTests(unittest.TestCase):
    def test_correct_slow_no_hint(self):
        r = score_attempt(True, False, 15.0)
        self.assertEqual(r.points_awarded, 100)
        self.assertFalse(r.fast_bonus_applied)

    def test_correct_fast_no_hint(self):
        r = score_attempt(True, False, 5.0)
        self.assertEqual(r.points_awarded, 110)
        self.assertTrue(r.fast_bonus_applied)

    def test_correct_fast_with_hint(self):
        r = score_attempt(True, True, 5.0)
        self.assertEqual(r.points_awarded, 100)  # +100 -10 +10

    def test_correct_slow_with_hint(self):
        r = score_attempt(True, True, 30.0)
        self.assertEqual(r.points_awarded, 90)  # +100 -10

    def test_wrong_answer(self):
        r = score_attempt(False, False, 3.0)
        self.assertEqual(r.points_awarded, -25)

    def test_wrong_answer_ignores_hint_and_speed(self):
        r = score_attempt(False, True, 2.0)
        self.assertEqual(r.points_awarded, -25)

    def test_negative_time_rejected(self):
        with self.assertRaises(ValueError):
            score_attempt(True, False, -1.0)

    def test_boundary_exactly_at_threshold_gets_bonus(self):
        r = score_attempt(True, False, 10.0)
        self.assertTrue(r.fast_bonus_applied)

    def test_boundary_just_over_threshold_no_bonus(self):
        r = score_attempt(True, False, 10.01)
        self.assertFalse(r.fast_bonus_applied)

    def test_accuracy_calc(self):
        self.assertEqual(compute_accuracy_percent(8, 2), 80.0)
        self.assertEqual(compute_accuracy_percent(0, 0), 0.0)

    def test_improvement_calc(self):
        self.assertEqual(compute_improvement_percent(52, 84), 32.0)


class RankTests(unittest.TestCase):
    def test_zero_score_is_newcomer(self):
        self.assertEqual(compute_rank(0), "Newcomer")

    def test_rank_thresholds_are_inclusive(self):
        self.assertEqual(compute_rank(300), "Cyber Learner")
        self.assertEqual(compute_rank(299), "Newcomer")

    def test_top_rank_reached(self):
        self.assertEqual(compute_rank(4500), "Cyber Champion")
        self.assertEqual(compute_rank(999_999), "Cyber Champion")

    def test_progress_toward_next_rank(self):
        progress = next_rank_progress(150)  # halfway from 0 to 300
        self.assertEqual(progress["name"], "Newcomer")
        self.assertEqual(progress["next_name"], "Cyber Learner")
        self.assertEqual(progress["percent_to_next"], 50.0)

    def test_progress_at_top_rank_is_100_percent(self):
        progress = next_rank_progress(10_000)
        self.assertIsNone(progress["next_name"])
        self.assertEqual(progress["percent_to_next"], 100.0)


class SecurityScoreTests(unittest.TestCase):
    def test_perfect_scores_yield_100(self):
        score = compute_security_score(
            accuracy_percent=100, levels_completed=5, total_levels=5,
            assessment_improvement=40,
        )
        self.assertEqual(score, 100)

    def test_zero_everything_yields_0(self):
        score = compute_security_score(
            accuracy_percent=0, levels_completed=0, total_levels=5,
            assessment_improvement=0,
        )
        self.assertEqual(score, 0)

    def test_missing_assessment_still_produces_a_score(self):
        score = compute_security_score(
            accuracy_percent=80, levels_completed=3, total_levels=5,
            assessment_improvement=None,
        )
        self.assertTrue(0 <= score <= 100)

    def test_score_is_deterministic(self):
        args = dict(accuracy_percent=72.5, levels_completed=2, total_levels=5, assessment_improvement=18)
        self.assertEqual(compute_security_score(**args), compute_security_score(**args))

    def test_classification_bands(self):
        self.assertEqual(classify_security_score(0), "Developing")
        self.assertEqual(classify_security_score(49), "Developing")
        self.assertEqual(classify_security_score(50), "Good")
        self.assertEqual(classify_security_score(75), "Strong")
        self.assertEqual(classify_security_score(90), "Excellent")


if __name__ == "__main__":
    unittest.main()
