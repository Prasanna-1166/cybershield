r"""
seed_all.py
-----------
WHAT: Seeds everything Phase 2-6 needs: 5 levels + 40 challenges, 8 badges,
      14 learning-center lessons, 12 assessment questions. Idempotent —
      safe to re-run; it skips anything that already exists by key.
WHERE: seed/seed_all.py
HOW TO RUN (Windows, venv activated, after seed_roles.py):
    python seed\seed_all.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.badge import Badge
from app.models.challenge import Challenge, ChallengeOption
from app.models.learning_content import LearningContent
from app.models.level import Level
from app.models.question import Question, QuestionOption
from seed.seed_data_badges import BADGES
from seed.seed_data_challenges import CHALLENGES_BY_LEVEL_KEY, LEVELS
from seed.seed_data_learning_content import LEARNING_CONTENT
from seed.seed_data_questions import QUESTIONS


def seed_levels_and_challenges():
    created_levels = 0
    created_challenges = 0

    for order_index, level_data in enumerate(LEVELS):
        level = Level.query.filter_by(key=level_data["key"]).first()
        if level is None:
            level = Level(
                number=level_data["number"], key=level_data["key"],
                name=level_data["name"], description=level_data["description"],
                order_index=order_index,
            )
            db.session.add(level)
            db.session.flush()  # get level.id without a full commit
            created_levels += 1

        existing_count = Challenge.query.filter_by(level_id=level.id).count()
        if existing_count > 0:
            continue  # this level's challenges were already seeded

        for order_index_c, c in enumerate(CHALLENGES_BY_LEVEL_KEY[level_data["key"]]):
            challenge = Challenge(
                level_id=level.id, order_index=order_index_c,
                scenario_type=c["scenario_type"], prompt=c["prompt"],
                question_text=c["question_text"], difficulty=c["difficulty"],
                hint_text=c["hint_text"], correct_explanation=c["correct_explanation"],
                warning_signs=c["warning_signs"], recommended_action=c["recommended_action"],
            )
            db.session.add(challenge)
            db.session.flush()
            for order_index_o, (text, is_correct) in enumerate(c["options"]):
                db.session.add(ChallengeOption(
                    challenge_id=challenge.id, order_index=order_index_o,
                    text=text, is_correct=is_correct,
                ))
            created_challenges += 1

    db.session.commit()
    return created_levels, created_challenges


def seed_badges():
    created = 0
    for b in BADGES:
        if not Badge.query.filter_by(key=b["key"]).first():
            db.session.add(Badge(key=b["key"], name=b["name"], icon=b["icon"], description=b["description"]))
            created += 1
    db.session.commit()
    return created


def seed_learning_content():
    created = 0
    for order_index, item in enumerate(LEARNING_CONTENT):
        if not LearningContent.query.filter_by(key=item["key"]).first():
            db.session.add(LearningContent(
                key=item["key"], category=item["category"], title=item["title"],
                what_is_it=item["what_is_it"], warning_signs=item["warning_signs"],
                example=item["example"], what_to_do=item["what_to_do"],
                order_index=order_index,
            ))
            created += 1
    db.session.commit()
    return created


def seed_questions():
    created = 0
    existing_count = Question.query.count()
    if existing_count > 0:
        return 0  # already seeded

    for item in QUESTIONS:
        question = Question(
            category=item["category"], text=item["text"], explanation=item["explanation"],
        )
        db.session.add(question)
        db.session.flush()
        for order_index_o, (text, is_correct) in enumerate(item["options"]):
            db.session.add(QuestionOption(
                question_id=question.id, order_index=order_index_o,
                text=text, is_correct=is_correct,
            ))
        created += 1

    db.session.commit()
    return created


def run():
    app = create_app(os.environ.get("FLASK_CONFIG", "development"))
    with app.app_context():
        levels, challenges = seed_levels_and_challenges()
        badges = seed_badges()
        lessons = seed_learning_content()
        questions = seed_questions()

        print(f"Levels created: {levels}")
        print(f"Challenges created: {challenges}")
        print(f"Badges created: {badges}")
        print(f"Learning-center lessons created: {lessons}")
        print(f"Assessment questions created: {questions}")
        print("Done. Safe to re-run — already-seeded items are skipped.")


if __name__ == "__main__":
    run()
