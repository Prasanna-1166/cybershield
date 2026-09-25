# CyberShield — Project Report

## Abstract

CyberShield is an interactive cybersecurity awareness, scam-detection, and
assistance platform built with Python, Flask, and MySQL. It combines
gamified training, rule-based detection tools, and structured incident
guidance into a single system organized around a PREVENT → DETECT → RESPOND
model. Unlike a standalone quiz application, CyberShield addresses two
distinct real-world gaps: users' difficulty recognizing realistic scam
attempts, and their uncertainty about what to do once a scam is suspected
or has already occurred. The platform measures learning outcomes through a
before/after assessment and generates a personalized report summarizing a
user's cybersecurity awareness.

## Introduction

Phishing, smishing, vishing, impersonation, and payment scams are
increasingly sophisticated, and general awareness that "scams exist" does
not reliably translate into recognizing a specific attempt in the moment.
Separately, users who do suspect something is wrong often lack a clear,
actionable next step. CyberShield was designed as a college final project
to demonstrate a full-stack, security-conscious solution to both problems
at once, rather than treating them as separate tools.

## Existing Problem

1. Awareness campaigns and one-off quizzes build abstract knowledge but
   don't train pattern recognition against realistic, varied scenarios.
2. Detection tools that do exist (spam filters, browser warnings) operate
   silently in the background and don't teach the user *why* something was
   flagged, so recognition skill doesn't transfer to channels the tool
   doesn't cover (e.g. SMS, WhatsApp).
3. Post-incident guidance is fragmented — users must separately discover
   what to do, who to contact, and where to report, often under stress and
   time pressure.

## Proposed Solution

CyberShield unifies three layers under one platform and one shared mental
model (PREVENT → DETECT → RESPOND):

- **Prevent:** a 5-level gamified training system that teaches through
  realistic (but entirely fictional) scenarios, with mandatory teaching
  feedback on every wrong answer.
- **Detect:** a rule-based Suspicious Message Analyzer and URL Safety
  Checker that give an on-demand, explainable second opinion, phrased
  probabilistically rather than as a certainty claim.
- **Respond:** a Cyber Help Center (12 dedicated scenarios) and an
  Incident Response Wizard that turn "what do I do now?" into a clear,
  step-by-step checklist, ending in official reporting links rather than
  CyberShield attempting to handle the report itself.

## Objectives

1. Teach recognition of phishing, suspicious URLs, weak password practices,
   and common scam patterns through interactive, scored training.
2. Provide safe, explainable, non-committal risk analysis for
   user-submitted messages and URLs.
3. Provide clear, structured incident-response guidance and route users to
   official government reporting resources.
4. Measure awareness improvement via a before/after assessment.
5. Demonstrate secure, OWASP-aligned full-stack development practices
   throughout — not just as an add-on.

## Scope

In scope: web-based training game, two rule-based analyzers, help-center
content, incident wizard, learning center, assessment + reporting,
leaderboard/badges, and an admin panel for content and user management.

Out of scope (explicitly, for safety): real phishing infrastructure,
malware, exploit code, password cracking, automated vulnerability scanning,
or automatically visiting/crawling user-submitted URLs.

## Functional Requirements

- User registration/login/logout with role-based access (USER/ADMIN).
- Play through 5 levels of scored, timed, hinted challenges.
- Submit free-text messages/URLs for rule-based risk analysis.
- Browse 12 help-center scenarios and a step-by-step incident wizard.
- Take a before/after assessment and view a personalized report.
- View a leaderboard and earned badges.
- Admin: manage users, toggle content active/inactive, view analytics.

## Non-Functional Requirements

- **Security:** hashed passwords, parameterized queries, CSRF protection,
  rate-limited auth endpoints, role-based authorization on every protected
  route, no secrets in source control, friendly error pages.
- **Usability:** responsive Bootstrap UI, beginner-friendly language,
  mobile-friendly layout, clear risk-level color coding.
- **Maintainability:** modular Flask Blueprints, a service layer decoupled
  from Flask/SQLAlchemy for the core logic (scoring, badges, analyzers),
  enabling unit testing without a database.
- **Performance:** designed to run comfortably on a standard Windows
  laptop with a local MySQL instance.

## System Architecture

```
Browser (Bootstrap + vanilla JS)
        │  HTTP
        ▼
Flask App Factory (app/__init__.py)
        │
        ├── Blueprints: main, auth, game, check, help, learn, admin
        │        │
        │        ▼
        │   Service layer (scoring, badge_rules, message_analyzer,
        │   url_checker, incident_wizard, game_service, badge_service,
        │   assessment_service, report_service) — pure logic, DB-agnostic
        │   where practical, so it's independently unit-testable.
        │
        ▼
SQLAlchemy ORM Models ──► MySQL (via PyMySQL)
```

Cross-cutting concerns (Flask-Login session auth, Flask-WTF CSRF,
Flask-Limiter rate limiting) are initialized once in `app/extensions.py`
and applied globally.

## Data Flow (DFD) Explanation

**Level 0 (context):** The User interacts with the CyberShield web app,
which reads/writes the MySQL database and never communicates with any
external service (no third-party API calls for the analyzers).

**Level 1 (major processes):**
1. *Authenticate* — validates credentials against `users`/`roles`.
2. *Play Training* — reads `levels`/`challenges`/`challenge_options`,
   writes `attempts`, recomputes `scores`, checks `badges`.
3. *Analyze Content* — pure computation over user input; writes only a
   privacy-safe summary to `analyzer_history` (never raw content).
4. *Get Help* — reads static scenario/wizard content; writes nothing
   sensitive (no incident details are persisted).
5. *Assess & Report* — reads `questions`/`question_options`, writes
   `assessment_attempts` and `reports`.
6. *Administer* — admin-only reads/writes across all content tables.

## ER Diagram Explanation

Core identity: `roles (1) ── (N) users`.

Training: `levels (1) ── (N) challenges (1) ── (N) challenge_options`;
`users (1) ── (N) attempts (N) ── (1) challenges`; `users (1) ── (1) scores`.

Badges: `badges (1) ── (N) user_badges (N) ── (1) users` (many-to-many via
join table, with a uniqueness constraint preventing duplicate awards).

Assessment: `questions (1) ── (N) question_options`; `users (1) ── (N)
assessment_attempts`.

Reporting/analytics: `users (1) ── (N) reports` (JSON snapshots);
`users (1) ── (N) analyzer_history` (nullable user_id — analyzers are
usable while logged out).

Content: `learning_content` is a standalone table with no foreign keys,
managed independently by admins.

## Database Design

15 tables total: `roles`, `users`, `levels`, `challenges`,
`challenge_options`, `attempts`, `scores`, `badges`, `user_badges`,
`learning_content`, `questions`, `question_options`,
`assessment_attempts`, `reports`, `analyzer_history`.

Design notes:
- `challenges`/`challenge_options` (training) are kept separate from
  `questions`/`question_options` (before/after assessment) because they
  serve different purposes — a challenge carries a scenario, hint, and
  full teaching payload; an assessment question is a plain scored item.
- `analyzer_history` intentionally never stores the raw analyzed text —
  only a short truncated preview, the risk level, and indicator count —
  per the spec's "don't store raw sensitive content unnecessarily" rule.
- `scores` is a maintained aggregate (not purely derived on read) so the
  leaderboard query stays cheap even as `attempts` grows.

## Modules

See README.md "What's actually in the app" for the full module-by-module
breakdown (Learn, Check, Cyber Help Center, Incident Response Wizard,
Official Resources, Learning Center, Assessment/Report, Dashboard,
Leaderboard, Badges, Admin Dashboard).

## Algorithms

**Scoring** (`app/services/scoring.py`): correct +100, wrong −25, hint −10,
fast-answer bonus (≤10s) +10, level completion +200 — computed server-side
from the submitted answer's correctness and elapsed time, never trusted
from the client.

**Message risk scoring** (`app/services/message_analyzer.py`): a weighted
rule set (regex pattern → indicator label → weight) is summed; three
tiers (LOW ≤3, MEDIUM ≤6, HIGH >6) with certain high-severity indicators
(OTP/password/KYC requests) additionally forcing at least MEDIUM on a
single hit.

**URL risk scoring** (`app/services/url_checker.py`): structural checks
only (HTTPS presence, raw IP, port, subdomain count, keyword matches,
shortener list, '@' trick, encoded characters, look-alike brand
detection via character-substitution matching, executable file paths),
summed and tiered the same way. Never resolves or fetches the URL.

**Badge eligibility** (`app/services/badge_rules.py`): a pure function
mapping a stats snapshot (per-level accuracy, fast-correct count, lessons
viewed, levels completed) plus already-earned badges to a set of newly
earned badge keys, including a "meta" badge awarded only once the other
seven are held.

## Security Practices

- Passwords hashed with salted PBKDF2-SHA256 (Werkzeug), never stored or
  logged in plaintext.
- All database access through SQLAlchemy's parameterized query API.
- CSRF protection applied globally (Flask-WTF), including on plain HTML
  forms, not just `FlaskForm`-rendered ones.
- Rate limiting on login and registration (Flask-Limiter).
- Generic authentication error messages (no user enumeration).
- `?next=` redirect validated to relative paths only (no open redirect).
- Role-based authorization via a single shared `admin_required` decorator.
- No secrets in source control — `SECRET_KEY` and DB credentials load from
  environment variables via `.env` (git-ignored), with `scripts/create_admin.py`
  interactively prompting for credentials instead of hard-coding them.
- Friendly error pages for 400/401/403/404/429/500 — no stack traces
  exposed to end users.
- Message/URL analyzers never call external APIs and never store raw
  sensitive input.

## Testing

75 automated tests across 8 files (`tests/`), covering: password-strength
rules, the scoring engine (including boundary conditions), badge
eligibility rules, the message analyzer and URL checker (against
realistic fictional scam text, verifying risk tiers and that no
certainty-claiming language is ever produced), the incident wizard's
urgency classification, registration/login/logout/authorization, and
route-level smoke tests for the game, analyzers, help center, learning
center, dashboard, leaderboard, report, and admin authorization
(including a check that a non-admin user is correctly blocked with 403).

Of these, the 49 tests with zero Flask/database dependency were executed
directly during development and caught two real defects before they
shipped (see README.md "How this was actually verified" for specifics).

## Results

The training game, both analyzers, the help center and wizard, the
learning center, the assessment/report flow, the leaderboard/badges, and
the admin panel are all implemented as real, working code — not
placeholders. Seed data provides 40 training challenges across 5 levels,
14 learning-center lessons, 12 assessment questions, and 8 badges, all
built from fictional organizations and safe example domains.

## Limitations

- Uses `db.create_all()` rather than versioned Flask-Migrate migrations for
  simplicity (Flask-Migrate is included as a dependency for future use).
- In-memory rate-limit storage is appropriate for local/demo use only.
- Admin content authoring currently supports activate/deactivate; adding
  new levels/lessons/questions is done via the `seed/` data files rather
  than a full in-browser content editor.
- The URL Checker's look-alike-domain detection uses a small, illustrative
  brand list and simple character-substitution rules — it is explicitly
  not a comprehensive typosquatting-detection system.

## Future Scope

- Flask-Migrate versioned migrations as the schema evolves.
- A full in-browser CRUD content editor for admins (beyond activate/deactivate).
- Expanded analyzer rule sets and/or an optional pluggable ML-based scorer.
- Localization for languages/regions beyond the current India-focused
  Official Resources content.
- Redis-backed rate limiting for multi-process production deployment.

## Conclusion

CyberShield demonstrates that a student project can go beyond a single
gamified quiz to become a genuinely useful, security-conscious platform
spanning prevention, detection, and response — while maintaining secure
coding practices, a normalized database design, and a real automated test
suite throughout.

## References

- OWASP Top Ten (owasp.org) — general secure-coding guidance followed
  throughout (parameterized queries, CSRF, secure session handling, etc.)
- Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Limiter official
  documentation.
- National Cyber Crime Reporting Portal, India — https://www.cybercrime.gov.in/
