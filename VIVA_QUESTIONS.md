# CyberShield — Viva Questions & Answers

## Concept / Positioning

**Q: Is this just a game?**
No. The gamified training is one module. CyberShield also has detection
tools (Message Analyzer, URL Checker) and response tools (Help Center,
Incident Response Wizard) — organized around a PREVENT → DETECT → RESPOND
model.

**Q: What real-world problem does this solve?**
Two gaps: (1) people struggle to recognize a *specific* realistic scam even
when they know scams exist in general, and (2) people who suspect a scam
often don't know what to do next. CyberShield trains recognition and gives
clear next steps.

**Q: Why not just use an existing spam filter?**
Spam filters work silently and don't teach the user anything, so the skill
doesn't transfer to channels they don't cover (SMS, WhatsApp, phone calls).
CyberShield explains *why* something is risky, building transferable
recognition skill.

## Architecture

**Q: Why did you use the "app factory" pattern instead of a single global
Flask app?**
`create_app()` lets you build a fresh, independently configured Flask app
per use case — one for `flask run`, a separate one per test — which is
what makes the automated test suite possible without touching the real
database.

**Q: Why is there a separate "services" layer?**
The core logic (scoring, badge eligibility, the analyzers, the incident
wizard's urgency classification) is written with zero Flask/SQLAlchemy
imports. That means it can be unit-tested directly, in isolation, without
spinning up a database — which is exactly how it was verified during
development.

**Q: Why Blueprints instead of one big routes file?**
Each feature area (auth, game, check, help, learn, admin) is a separate
Blueprint, so routes are modular, easier to navigate, and each Blueprint
can be reasoned about independently.

## Database

**Q: Why are `challenges` and `questions` separate tables instead of one?**
They serve different purposes: a `challenge` (used by the training game)
carries a scenario, a hint, and full teaching content; a `question` (used
by the before/after assessment) is a plain scored quiz item. Keeping them
separate is more normalized and avoids overloading one table with two
different shapes of data.

**Q: Why doesn't `analyzer_history` store the message/URL text that was
analyzed?**
Per the safety requirement not to store raw sensitive content
unnecessarily — only a short, truncated, non-reversible preview plus the
risk level and indicator count are stored, which is enough for a user's
own history view without retaining sensitive text long-term.

**Q: How is score integrity protected — can a user submit a fake score?**
No. The client only submits which option it selected and hint-usage; the
server looks up the actual correct answer and the actual elapsed time,
and computes the score itself (`app/services/scoring.py`). A tampered
client request can't change what points are awarded.

## Security

**Q: How are passwords stored?**
Hashed with Werkzeug's `generate_password_hash`, which uses salted
PBKDF2-SHA256 by default — never stored or logged in plaintext, and the
salt means two users with the same password get different hashes.

**Q: How is CSRF handled?**
Flask-WTF's `CSRFProtect` is applied globally to the whole app, so every
POST request — including plain HTML forms that don't use a `FlaskForm`
object — requires a valid CSRF token.

**Q: How is SQL injection prevented?**
All database access goes through SQLAlchemy's ORM query API, which
parameterizes values automatically. There is no raw, string-concatenated
SQL anywhere in the codebase.

**Q: How is admin access restricted?**
A single `admin_required` decorator (in `app/routes/decorators.py`) wraps
every admin route, checking `current_user.is_admin`. Centralizing this in
one decorator means every admin route gets the same correct check, rather
than relying on each route remembering to add it.

**Q: What happens if a user tries to brute-force a login?**
Flask-Limiter caps login attempts (10/minute) and registration (5/minute).
Login error messages are also deliberately generic ("Invalid
username/email or password") so an attacker can't tell whether a
particular username or email exists in the system.

## Detection Modules

**Q: Why doesn't the Message Analyzer say "this IS a scam"?**
Because a rule-based heuristic can't be certain — false positives and
false negatives are both possible. It always uses probabilistic language
("indicators commonly associated with...") and shows a visible disclaimer,
to avoid over-trusting or under-trusting the tool.

**Q: Does the URL Checker actually visit the URL to check it?**
No — never. It only analyzes the URL as a text string (structure, host,
path, encoding). Automatically visiting a possibly-malicious URL would
itself be a safety risk, so that's a hard rule, not just an optimization.

**Q: How does the Message Analyzer decide the risk level?**
A fixed set of regex-based rules, each with a label and a weight, scans
the text. Matched weights are summed; certain high-severity categories
(OTP requests, password/PIN requests, KYC impersonation) additionally
force at least a MEDIUM rating on a single match. Thresholds then map the
total score to LOW/MEDIUM/HIGH.

## Response Modules

**Q: Does CyberShield file a cybercrime report for the user?**
No — explicitly not. The Incident Response Wizard and Help Center give
guidance and then link out to the real, official National Cyber Crime
Reporting Portal and the 1930 helpline. CyberShield never imitates the
government portal's UI and never claims to submit anything on the user's
behalf.

**Q: How is "urgency" determined in the Incident Wizard, and is it
authoritative?**
It's a simple, transparent mapping from the selected "what happened"
option to LOW/MODERATE/URGENT (e.g. money transferred or an OTP shared →
URGENT). It's explicitly labeled educational only, not professional or
legal advice.

## Testing

**Q: How much of this was actually tested, and how?**
75 automated tests across 8 files. The core logic — password rules,
scoring, badge eligibility, both analyzers, and the incident wizard's
classifier — has zero Flask/database dependency by design, so those 49
tests were run directly and independently of the rest of the stack.
Route-level tests (registration/login/game-play/analyzers/help
center/admin authorization) exercise the full Flask+DB stack using an
in-memory SQLite database reserved for testing only.

**Q: Why SQLite for tests if the app uses MySQL?**
It's a test-only substitution for speed and isolation — the shipped app's
`DATABASE_URL` still targets MySQL; only the automated test suite swaps in
an in-memory database so tests run fast and never touch real data.

## Badges / Gamification

**Q: How does badge logic actually work — is it hardcoded per user?**
No. `app/services/badge_rules.py` is a pure function: given a stats
snapshot (per-level accuracy, fast-correct count, lessons viewed, levels
completed) and the set of badges already earned, it returns exactly the
newly-earned badge keys. This is unit-tested directly, including edge
cases like the "meta" Champion badge only unlocking once all seven other
badges are held.
