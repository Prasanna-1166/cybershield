"""
badge_rules.py
--------------
WHAT: Pure functions deciding which badges a user has newly earned, given a
      plain dict of their current stats. No Flask/SQLAlchemy imports here —
      app/services/badge_service.py builds the stats dict from the DB and
      calls into this module, which keeps the actual "business rule" part
      unit-testable in isolation (see tests/test_badges.py).
WHERE: app/services/badge_rules.py

Badge keys (must match seed/seed_badges.py):
    phishing_hunter, url_detective, password_protector, scam_spotter,
    fast_thinker, cyber_learner, security_expert, cybershield_champion

Rules (assumptions, documented per project working rules — a reasonable
beginner-friendly interpretation of "real backend badge logic"):
    phishing_hunter        -> Level 1 completed with 100% accuracy on it
    url_detective          -> Level 2 completed with 100% accuracy on it
    password_protector     -> Level 3 completed with 100% accuracy on it
    scam_spotter           -> Level 4 completed with 100% accuracy on it
    fast_thinker           -> 5+ correct answers earned the fast-answer bonus
    cyber_learner          -> viewed 5+ distinct Learning Center lessons
    security_expert        -> all 5 levels completed
    cybershield_champion   -> all 7 other badges earned
"""

ALL_BADGE_KEYS = [
    "phishing_hunter",
    "url_detective",
    "password_protector",
    "scam_spotter",
    "fast_thinker",
    "cyber_learner",
    "security_expert",
    "cybershield_champion",
]

_LEVEL_PERFECT_BADGE_BY_NUMBER = {
    1: "phishing_hunter",
    2: "url_detective",
    3: "password_protector",
    4: "scam_spotter",
}


def evaluate_badges(stats: dict, already_earned: set) -> set:
    """
    stats expects keys:
        level_accuracy: dict[int, float]   e.g. {1: 100.0, 2: 80.0}
        levels_completed: int
        fast_correct_count: int
        distinct_lessons_viewed: int
    already_earned: set of badge keys the user already has.

    Returns: set of NEWLY earned badge keys (does not include already_earned).
    """
    newly_earned = set()
    level_accuracy = stats.get("level_accuracy", {})

    for level_number, badge_key in _LEVEL_PERFECT_BADGE_BY_NUMBER.items():
        if badge_key in already_earned:
            continue
        if level_accuracy.get(level_number, 0) >= 100.0:
            newly_earned.add(badge_key)

    if "fast_thinker" not in already_earned and stats.get("fast_correct_count", 0) >= 5:
        newly_earned.add("fast_thinker")

    if "cyber_learner" not in already_earned and stats.get("distinct_lessons_viewed", 0) >= 5:
        newly_earned.add("cyber_learner")

    if "security_expert" not in already_earned and stats.get("levels_completed", 0) >= 5:
        newly_earned.add("security_expert")

    # Champion depends on the union of previously-earned + just-earned badges.
    combined = already_earned | newly_earned
    other_seven = set(ALL_BADGE_KEYS) - {"cybershield_champion"}
    if "cybershield_champion" not in already_earned and other_seven.issubset(combined):
        newly_earned.add("cybershield_champion")

    return newly_earned
