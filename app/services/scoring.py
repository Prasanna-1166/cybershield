"""
scoring.py
----------
WHAT: The pure scoring math for the training game — deliberately has ZERO
      Flask/SQLAlchemy imports so it can be unit-tested in total isolation
      (see tests/test_scoring.py) and reused safely by game_service.py.
WHY:  Scoring rules from the spec:
        correct answer:      +100
        wrong answer:         -25
        hint used:            -10 (in addition to the above)
        fast-answer bonus:    +10 (correct AND answered within threshold)
        level completion:    +200 (awarded once, elsewhere, when all
                                    challenges in a level are passed)
      All of this must be recomputed server-side from the submitted answer
      and timing — never trust a client-submitted score.
WHERE: app/services/scoring.py
"""

from dataclasses import dataclass

POINTS_CORRECT = 100
POINTS_WRONG = -25
POINTS_HINT_PENALTY = -10
POINTS_FAST_BONUS = 10
POINTS_LEVEL_COMPLETE = 200

FAST_ANSWER_THRESHOLD_SECONDS = 10.0


@dataclass
class ScoreResult:
    is_correct: bool
    points_awarded: int
    fast_bonus_applied: bool
    hint_penalty_applied: bool


def score_attempt(
    is_correct: bool,
    used_hint: bool,
    response_time_seconds: float,
) -> ScoreResult:
    """
    Computes the points for a single challenge attempt.

    Rules (in order):
      - Wrong answer -> -25 points, no other bonuses/penalties apply on top
        (a wrong-but-fast answer doesn't get the fast bonus; a wrong answer
        with a hint doesn't get double-penalized beyond the wrong-answer cost).
      - Correct answer -> +100, then:
          -10 if a hint was used
          +10 if answered within FAST_ANSWER_THRESHOLD_SECONDS (and no hint
              penalty logically prevents the fast bonus — they're independent)
    """
    if response_time_seconds < 0:
        raise ValueError("response_time_seconds cannot be negative")

    if not is_correct:
        return ScoreResult(
            is_correct=False,
            points_awarded=POINTS_WRONG,
            fast_bonus_applied=False,
            hint_penalty_applied=False,
        )

    points = POINTS_CORRECT
    hint_penalty_applied = False
    fast_bonus_applied = False

    if used_hint:
        points += POINTS_HINT_PENALTY
        hint_penalty_applied = True

    if response_time_seconds <= FAST_ANSWER_THRESHOLD_SECONDS:
        points += POINTS_FAST_BONUS
        fast_bonus_applied = True

    return ScoreResult(
        is_correct=True,
        points_awarded=points,
        fast_bonus_applied=fast_bonus_applied,
        hint_penalty_applied=hint_penalty_applied,
    )


def level_completion_bonus() -> int:
    return POINTS_LEVEL_COMPLETE


def compute_accuracy_percent(correct_count: int, wrong_count: int) -> float:
    total = correct_count + wrong_count
    if total == 0:
        return 0.0
    return round((correct_count / total) * 100, 1)


def compute_improvement_percent(before_percent: float, after_percent: float) -> float:
    """Used by the Before/After Assessment (Part H). Returns a signed
    percentage-point difference, e.g. 52 -> 84 gives +32.0."""
    return round(after_percent - before_percent, 1)


# ---------------------------------------------------------------------------
# Rank system — a friendlier label over total_score than the raw number.
# Deterministic and pure (same inputs always give the same rank), so it's
# fully unit-testable without touching the database.
# ---------------------------------------------------------------------------

RANKS = [
    (0, "Newcomer"),
    (300, "Cyber Learner"),
    (800, "Security Aware"),
    (1600, "Security Defender"),
    (2800, "Cyber Guardian"),
    (4500, "Cyber Champion"),
]


def compute_rank(total_score: int) -> str:
    """Returns the highest rank name whose threshold total_score has met."""
    rank_name = RANKS[0][1]
    for threshold, name in RANKS:
        if total_score >= threshold:
            rank_name = name
        else:
            break
    return rank_name


def next_rank_progress(total_score: int) -> dict:
    """Returns {name, next_name, next_threshold, percent_to_next} describing
    progress toward the next rank, for a progress bar on the dashboard.
    percent_to_next is 100 once the highest rank is reached."""
    current_name = compute_rank(total_score)
    for i, (threshold, name) in enumerate(RANKS):
        if name == current_name:
            current_index = i
            break

    if current_index == len(RANKS) - 1:
        return {
            "name": current_name,
            "next_name": None,
            "next_threshold": None,
            "percent_to_next": 100.0,
        }

    current_threshold = RANKS[current_index][0]
    next_threshold, next_name = RANKS[current_index + 1]
    span = next_threshold - current_threshold
    progressed = total_score - current_threshold
    percent = 0.0 if span <= 0 else round(min(100.0, max(0.0, progressed / span * 100)), 1)

    return {
        "name": current_name,
        "next_name": next_name,
        "next_threshold": next_threshold,
        "percent_to_next": percent,
    }


# ---------------------------------------------------------------------------
# Cyber Safety Score — a single 0-100 number combining training accuracy,
# training breadth (levels completed), and assessment improvement. Every
# input is a real, already-computed metric from the database — nothing here
# invents data. See app/services/report_service.py for where it's used.
# ---------------------------------------------------------------------------

SCORE_CLASSIFICATIONS = [
    (0, "Developing"),
    (50, "Good"),
    (75, "Strong"),
    (90, "Excellent"),
]


def compute_security_score(
    accuracy_percent: float,
    levels_completed: int,
    total_levels: int,
    assessment_improvement: float | None,
) -> int:
    """Weighted blend, each component already 0-100 before weighting:
      - 55% training accuracy (how often the user picks the right answer)
      - 25% training breadth (how many levels completed out of the total)
      - 20% assessment improvement, capped at +40 percentage points mapped
        to 0-100 (no assessment yet -> this component is simply omitted and
        the other two are re-weighted proportionally, not zeroed out).
    """
    accuracy_component = max(0.0, min(100.0, accuracy_percent))
    breadth_component = 0.0
    if total_levels > 0:
        breadth_component = max(0.0, min(100.0, (levels_completed / total_levels) * 100))

    if assessment_improvement is None:
        # Re-weight the two available components to still sum to 100%.
        weighted = accuracy_component * (55 / 80) + breadth_component * (25 / 80)
    else:
        improvement_component = max(0.0, min(100.0, (assessment_improvement / 40) * 100))
        weighted = (
            accuracy_component * 0.55
            + breadth_component * 0.25
            + improvement_component * 0.20
        )

    return round(max(0, min(100, weighted)))


def classify_security_score(score: int) -> str:
    classification = SCORE_CLASSIFICATIONS[0][1]
    for threshold, name in SCORE_CLASSIFICATIONS:
        if score >= threshold:
            classification = name
        else:
            break
    return classification
