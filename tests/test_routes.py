"""
test_routes.py
---------------
Route-level tests covering Phases 2-6: the training game (answer submission
+ scoring + badges), the analyzers, the help center + wizard, the learning
center, the dashboard/leaderboard/report, and admin authorization.

Uses TestingConfig (in-memory SQLite) — same approach as test_auth.py.
Seeds a minimal dataset directly (not the full seed/ scripts) to keep each
test fast and self-contained.

Run with: python -m unittest tests.test_routes -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.badge import Badge
from app.models.challenge import Challenge, ChallengeOption
from app.models.learning_content import LearningContent
from app.models.level import Level
from app.models.question import Question, QuestionOption
from app.models.role import ROLE_ADMIN, ROLE_USER, Role


class RouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        db.session.add(Role(name=ROLE_USER))
        db.session.add(Role(name=ROLE_ADMIN))
        db.session.commit()

        self._seed_minimal_content()

        self.register_and_login("alice", "alice@example.com")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # ------------------------------------------------------------------
    def _seed_minimal_content(self):
        level1 = Level(number=1, key="phishing_hunter", name="Phishing Hunter",
                        description="Test level", order_index=0)
        db.session.add(level1)
        db.session.flush()

        challenge = Challenge(
            level_id=level1.id, order_index=0, scenario_type="email",
            prompt="Test scenario prompt", question_text="Is this safe?",
            difficulty="easy", hint_text="Look carefully.",
            correct_explanation="Because X.", warning_signs="Sign one\nSign two",
            recommended_action="Do not click.",
        )
        db.session.add(challenge)
        db.session.flush()
        self.correct_option = ChallengeOption(challenge_id=challenge.id, order_index=0, text="Correct", is_correct=True)
        self.wrong_option = ChallengeOption(challenge_id=challenge.id, order_index=1, text="Wrong", is_correct=False)
        db.session.add_all([self.correct_option, self.wrong_option])

        db.session.add(LearningContent(
            key="phishing", category="phishing", title="Phishing",
            what_is_it="...", warning_signs="...", example="...", what_to_do="...",
            order_index=0,
        ))

        question = Question(category="phishing", text="Test question?", explanation="Because.")
        db.session.add(question)
        db.session.flush()
        db.session.add(QuestionOption(question_id=question.id, order_index=0, text="Right", is_correct=True))
        db.session.add(QuestionOption(question_id=question.id, order_index=1, text="Wrong", is_correct=False))

        db.session.add(Badge(key="phishing_hunter", name="Phishing Hunter", icon="🎣", description="Test badge"))

        db.session.commit()
        self.challenge_id = challenge.id
        self.level = level1

    def register_and_login(self, username, email, password="Str0ng!Passw0rd"):
        self.client.post("/auth/register", data={
            "username": username, "email": email,
            "password": password, "confirm_password": password,
        }, follow_redirects=True)
        self.client.post("/auth/login", data={"identifier": username, "password": password})

    # ------------------------------------------------------------------
    # Game
    # ------------------------------------------------------------------
    def test_levels_page_loads(self):
        resp = self.client.get("/play/")
        self.assertEqual(resp.status_code, 200)

    def test_play_level_loads_challenge(self):
        resp = self.client.get("/play/level/1")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Is this safe?", resp.data)

    def test_correct_answer_awards_points_and_badge(self):
        self.client.get("/play/level/1")  # sets session timer
        resp = self.client.post(
            f"/play/answer/{self.challenge_id}",
            data={"option_id": self.correct_option.id, "used_hint": "0"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Correct", resp.data)
        # Only 1 challenge in this level, so it's the only one to complete —
        # 100% accuracy should award the phishing_hunter badge too.
        self.assertIn(b"badge", resp.data.lower())

    def test_wrong_answer_still_teaches(self):
        self.client.get("/play/level/1")
        resp = self.client.post(
            f"/play/answer/{self.challenge_id}",
            data={"option_id": self.wrong_option.id, "used_hint": "0"},
            follow_redirects=True,
        )
        self.assertIn(b"Security principle", resp.data)
        self.assertIn(b"What you should have noticed", resp.data)

    # ------------------------------------------------------------------
    # Check (analyzers)
    # ------------------------------------------------------------------
    def test_message_analyzer_get(self):
        resp = self.client.get("/check/message")
        self.assertEqual(resp.status_code, 200)

    def test_message_analyzer_post(self):
        resp = self.client.post("/check/message", data={"message_text": "hello there"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Risk Level", resp.data)

    def test_url_checker_post(self):
        resp = self.client.post("/check/url", data={"url_text": "https://example.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Risk Level", resp.data)

    # ------------------------------------------------------------------
    # Help center / wizard / resources
    # ------------------------------------------------------------------
    def test_help_index_lists_scenarios(self):
        resp = self.client.get("/help/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"I Need Cyber Help", resp.data)

    def test_help_scenario_page(self):
        resp = self.client.get("/help/scenario/lost-money")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"1930", resp.data)

    def test_help_scenario_404_for_unknown_key(self):
        resp = self.client.get("/help/scenario/not-a-real-scenario")
        self.assertEqual(resp.status_code, 404)

    def test_wizard_urgent_flow(self):
        resp = self.client.post("/help/wizard", data={"what_happened": "money_transferred"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"URGENT", resp.data)
        self.assertIn(b"1930", resp.data)

    def test_official_resources_page(self):
        resp = self.client.get("/help/resources")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"cybercrime.gov.in", resp.data)

    # ------------------------------------------------------------------
    # Learning center
    # ------------------------------------------------------------------
    def test_learn_index(self):
        resp = self.client.get("/learn/")
        self.assertEqual(resp.status_code, 200)

    def test_learn_lesson_page(self):
        resp = self.client.get("/learn/phishing")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"What is it?", resp.data)

    # ------------------------------------------------------------------
    # Dashboard / leaderboard / report
    # ------------------------------------------------------------------
    def test_dashboard_loads(self):
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)

    def test_leaderboard_loads_without_email(self):
        resp = self.client.get("/leaderboard")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(b"alice@example.com", resp.data)

    def test_report_loads(self):
        resp = self.client.get("/report")
        self.assertEqual(resp.status_code, 200)

    def test_report_pdf_downloads(self):
        resp = self.client.get("/report/pdf")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "application/pdf")
        self.assertTrue(resp.data.startswith(b"%PDF"))

    # ------------------------------------------------------------------
    # Admin authorization
    # ------------------------------------------------------------------
    def test_regular_user_cannot_access_admin(self):
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 403)

    def test_admin_user_can_access_admin(self):
        self.client.get("/auth/logout")
        admin_role = Role.query.filter_by(name=ROLE_ADMIN).first()
        from app.models.user import User
        admin = User(username="adminuser", email="admin@example.com", role=admin_role)
        admin.set_password("Str0ng!Passw0rd")
        db.session.add(admin)
        db.session.commit()
        self.client.post("/auth/login", data={"identifier": "adminuser", "password": "Str0ng!Passw0rd"})
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
