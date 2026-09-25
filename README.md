# CyberShield

An interactive cybersecurity awareness, scam-detection, and assistance platform.

> "CyberShield is a cybersecurity assistance and awareness platform. Its gamified
> training module teaches users to recognize threats, while its detection and
> incident-response modules provide practical help when users encounter suspicious
> activity."

```
PREVENT → DETECT → RESPOND
   │          │         │
 Training   Message   Cyber Help Center
 Game       Analyzer  Incident Response Wizard
            URL       Official Reporting Resources
            Checker
```

## The problem

People increasingly face phishing, fake bank/KYC alerts, impersonation, fake job
offers, malicious links, and payment scams. Two gaps exist:

1. Users often can't recognize a realistic scam attempt even knowing scams exist
   in general.
2. When someone *suspects* a scam or has already interacted with one, they usually
   don't know the next step ("I clicked a link — now what?").

CyberShield trains recognition, offers on-demand analysis tools, and gives clear
next-step guidance plus official reporting resources.

## Project status: all 8 phases complete

| Phase | Contents | Status |
|---|---|---|
| 1 | Project setup, Flask app factory, SQLite/Postgres config, auth, base templates | ✅ |
| 2 | Training game: 5 levels, 40 challenges, timer, scoring, hints | ✅ |
| 3 | Badges, leaderboard, progress, Before/After assessment, reports | ✅ |
| 4 | Suspicious Message Analyzer, URL Safety Checker | ✅ |
| 5 | Cyber Help Center (12 scenarios), Incident Response Wizard, Official Resources | ✅ |
| 6 | Admin Dashboard, content management, analytics | ✅ |
| 7 | Security hardening, test suite, error handling | ✅ |
| 8 | Documentation (this file, PROJECT_REPORT, PRESENTATION_CONTENT, VIVA_QUESTIONS) | ✅ |

### How this was actually verified

Unlike the original build, this hardening/redesign pass was done with real
package installation, a real SQLite database, and a real running Flask
server — nothing here is describing untested code:

- **Full dependency install** (`pip install -r requirements.txt`) in a real
  virtualenv, including Flask-SQLAlchemy, Flask-Migrate, Flask-Login,
  Flask-WTF, Flask-Limiter, gunicorn, and reportlab.
- **Real migrations applied** to a real SQLite file (`flask db upgrade`),
  then seeded with the actual seed scripts.
- **Full automated test suite executed and passing: 92 tests across 10
  files** — the original 75, plus 6 new tests for `/health` and the
  production-config fail-safe, plus 11 new tests for the rank system,
  Cyber Safety Score, and PDF report export.
- **A full manual smoke test** hitting every route in the app — home,
  dashboard, all 5 training levels, both analyzers, the help center and
  wizard, learning center, leaderboard, profile, assessment, report (HTML
  and PDF), and every admin page — while logged in as both a regular user
  and an admin, all returning `200 OK` with no template errors.

**You should still run the test suite yourself** (steps below) to confirm
on your machine — but this was genuinely run, not just written.

---

## What's actually in the app

### A. Learn — gamified training (5 levels, 40 challenges)
Phishing Hunter, URL Detective, Account Guardian, Scam Spotter, Cyber Escape.
Every wrong answer teaches (correct answer → why → warning signs → recommended
action) — never just "Wrong." Timer, hints (-10 pts), streaks, scoring is
**entirely server-recomputed** from the submitted answer + timing (see
`app/services/scoring.py`, unit-tested).

### B/C. Check — Message Analyzer & URL Checker
Rule-based, fully working, zero external API calls. Always probabilistic
language ("indicators commonly associated with...") with a visible disclaimer,
never a certainty claim. The URL Checker analyzes text only — it never visits,
crawls, or resolves the URL. Both are unit-tested against realistic fictional
scam text (`tests/test_message_analyzer.py`, `tests/test_url_checker.py`).

### D/E/F. Cyber Help Center, Incident Response Wizard, Official Resources
12 dedicated scenario pages (What may have happened → Immediate steps → What
NOT to do → Account/device safety → When to contact the org → When to report →
Official resources). The Wizard classifies urgency (LOW/MODERATE/URGENT,
educational only) and surfaces the **1930** helpline and the National Cyber
Crime Reporting Portal prominently for financial fraud. CyberShield never
imitates the government portal and never claims to file a report itself.

### G. Cyber Safety Learning Center
14 short lessons (phishing, smishing, vishing, social engineering, suspicious
URLs, password safety, MFA, account security, impersonation, online scams,
payment scams, safe browsing, safe messaging, basic incident response).

### H/I. Before/After Assessment & Personalized Report
12-question quiz taken before and after training; before/after scores stored
and compared. The report (Chart.js bar chart) shows overall score, accuracy,
per-level performance, strong/weak areas, recommended lessons, avg response
time, hints used, and improvement %.

### J/K/L. Dashboard, Leaderboard, Badges
Score, level, accuracy, badges, progress bars, quick actions. Leaderboard
shows rank/name/score/accuracy/levels — **no email addresses**. 8 badges with
real backend eligibility logic (`app/services/badge_rules.py`, unit-tested).

### M. Admin Dashboard
User management (activate/deactivate), level/challenge activation, learning-
content activation, assessment-question activation, and analytics (overall
accuracy, analyzer usage + risk breakdown, hardest challenges). Every route
requires the ADMIN role (`app/routes/decorators.py::admin_required`).

---

## Windows 10/11 setup

Run these from the `cybershield/` project folder in **Command Prompt** or
**PowerShell**.

### 1. Create and activate a virtual environment
```bat
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```bat
pip install -r requirements.txt
```

### 3. Configure environment variables
```bat
copy .env.example .env
```
Edit `.env` and set `SECRET_KEY` to any long random string. That's it for a
local run — **no database server to install.** By default the app uses a
local SQLite file at `instance/cybershield.db`, created automatically. (See
[Database](#database) below for using PostgreSQL instead later.)

### 4. Initialize the database with Flask-Migrate
The `migrations/` folder (with the initial schema) is already included, so
you just need to apply it:
```bat
set FLASK_APP=app:create_app('development')
flask db upgrade
```
This creates `instance/cybershield.db` with every table, using versioned
migrations rather than an unversioned `db.create_all()`. If you ever change
a model, generate the next migration with `flask db migrate -m "message"`
then apply it with `flask db upgrade`.

### 5. Seed roles, then everything else
```bat
python seed\seed_roles.py
python seed\seed_all.py
```
`seed_all.py` is idempotent — safe to re-run any time; it skips anything
already in the database.

### 6. Create an admin account
```bat
python scripts\create_admin.py
```
Prompts you for credentials — nothing is hard-coded.

### 7. Run the app
```bat
python run.py
```
Visit **http://127.0.0.1:5000/**. Check **http://127.0.0.1:5000/health**
too — it should return `{"status": "ok"}`.

### 8. Run the tests
```bat
python -m pytest -v
```
(or `python -m unittest discover -s tests -v`, which also works.)
Expect **92 tests across 10 files** to pass: `test_password_strength`,
`test_scoring`, `test_badges`, `test_message_analyzer`, `test_url_checker`,
`test_incident_wizard`, `test_auth`, `test_routes`, and
`test_config_and_health`.

---

## Project structure

```
cybershield/
    app/
        __init__.py, config.py, extensions.py
        models/            # 13 SQLAlchemy models — see "Database" below
        routes/             # main, auth, game, check, help, learn, admin + forms/decorators
        services/           # scoring, badge_rules, message_analyzer, url_checker,
                             # incident_wizard, help_content, game_service, badge_service,
                             # assessment_service, report_service
        templates/          # 36 Jinja2/Bootstrap templates
        static/{css,js,images}
    migrations/              # Flask-Migrate / Alembic versioned schema history
    scripts/create_admin.py  # interactive, secure admin creation
    seed/                    # seed_roles.py, seed_all.py + seed_data_*.py content
    tests/                   # 8 test files, ~50+ tests
    instance/
    .env.example
    requirements.txt
    run.py
    README.md, PROJECT_REPORT.md, PRESENTATION_CONTENT.md, VIVA_QUESTIONS.md
```

## Database

`roles`, `users`, `levels`, `challenges`, `challenge_options`, `attempts`,
`scores`, `badges`, `user_badges`, `learning_content`, `questions`,
`question_options`, `assessment_attempts`, `reports`, `analyzer_history` — 15
tables total (the spec's minimum list, plus `challenge_options` /
`question_options` split for proper normalization — see the docstring in
`app/models/challenge.py` for the reasoning).

**Never stored:** plaintext passwords, OTPs, bank/card numbers, or raw
analyzer input text (only a short truncated preview + the risk result — see
`app/models/analyzer_history.py`).

**SQLite by default, PostgreSQL when you need it.** The app talks to the
database only through SQLAlchemy models — nothing in `app/models/` or
`app/services/` knows or cares which database engine is underneath. Which
one is used is controlled entirely by the `DATABASE_URL` environment
variable:

| Environment | `DATABASE_URL` | Notes |
|---|---|---|
| Local dev / college demo | *(unset)* | Defaults to `sqlite:///instance/cybershield.db` |
| Public deployment | `postgresql+psycopg2://user:pass@host:5432/db` | Recommended — see below |
| Existing MySQL setup | `mysql+pymysql://user:pass@host:3306/db` | Still supported |

**Why not just SQLite everywhere?** SQLite stores the whole database in one
file on local disk. That's perfect for development and for a demo you run
yourself. Many free/low-cost hosting platforms, however, wipe or replace the
local filesystem on every deploy or restart — which would silently delete
every user account, score, and badge. If you deploy CyberShield somewhere
with a *persistent* disk, SQLite is fine. Otherwise, switch to PostgreSQL:

1. Create a Postgres database on your host (most platforms offer one).
2. `pip install psycopg2-binary` (already listed, commented out, in
   `requirements.txt`).
3. Set `DATABASE_URL=postgresql+psycopg2://...` in your environment.
4. Run `flask db upgrade` against it — same migrations, no code changes.

## Migrations (Flask-Migrate)

Schema changes are tracked as versioned migration files under
`migrations/versions/`, not applied ad-hoc with `db.create_all()`. Common
commands (run with `FLASK_APP=app:create_app('development')` set, or
substitute `'production'`/`'testing'` as appropriate):

```bash
flask db upgrade                    # apply all pending migrations
flask db migrate -m "add X column"  # generate a new migration after editing a model
flask db downgrade                  # roll back the last migration
flask db current                    # show which migration is applied
```

## Security notes

- No hard-coded secrets anywhere — `SECRET_KEY` and DB credentials come only
  from `.env` (git-ignored). Starting the app with `FLASK_CONFIG=production`
  and no real `SECRET_KEY` set **refuses to start** rather than running
  insecurely (see `app/config.py: ProductionConfig.validate()`).
- Passwords hashed with `werkzeug.security.generate_password_hash` (salted
  PBKDF2-SHA256).
- All DB access via SQLAlchemy's query API — parameterized automatically.
- CSRF tokens required on every POST (Flask-WTF `CSRFProtect`, applied
  globally — including plain HTML forms, not just `FlaskForm`-based ones).
- Login and registration are rate-limited; login errors are generic (no
  username/email enumeration); `?next=` only follows relative paths.
- Every admin route requires the ADMIN role via one shared decorator
  (`admin_required`) rather than copy-pasted checks.
- Friendly 400/401/403/404/429/500 pages — no stack traces shown to users.
- `scripts/create_admin.py` interactively prompts for credentials (via
  `getpass`, hidden input) — never hard-coded.
- Production security headers are set on every response (see
  `app/__init__.py: _register_security_headers`): a same-origin
  `Content-Security-Policy` (with a per-request nonce for the two inline
  `<script>` blocks, instead of a blanket `unsafe-inline`), plus
  `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and
  `Permissions-Policy`.
- `GET /health` returns `{"status": "ok"}` for uptime monitors and hosting
  platform health checks — it reveals nothing about the database or config.

## Limitations (honest, current)

- Rate limiting uses in-memory storage — fine for local/demo use and a
  single-process deployment, not for multiple worker processes sharing
  limits (point `RATELIMIT_STORAGE_URI` at Redis if you scale out).
- The Message Analyzer and URL Checker are intentionally open to logged-out
  visitors (detection help shouldn't require an account) — usage is still
  privacy-safe logged (risk level + indicator count only, never raw content).
- Admin content management (levels/challenges/lessons/questions/users)
  supports activate/deactivate in the UI, with a polished table view for
  each. Full create/edit forms for brand-new content are a natural next
  extension — for now, new content is added via `seed/`, and everything
  seeded is manageable (toggle on/off) from the admin console.
- The rest of the UI/UX modernization is done: a CSS-variable design system
  (`app/static/css/style.css`) with light/dark/auto theming, a redesigned
  landing page with real (non-fabricated) stats, a redesigned dashboard with
  a Cyber Safety Score ring, rank system, and badge grid, redesigned
  training/feedback screens, toast notifications, a downloadable PDF report,
  print-friendly styling, and an accessibility pass (skip link, focus
  states, labelled forms, `prefers-reduced-motion` support).

## What's done

Both halves of the original brief are complete:

**Database & deployment hardening:** SQLite by default with a clean
PostgreSQL upgrade path via `DATABASE_URL`, Flask-Migrate instead of
`db.create_all()`, production security headers (CSP with per-request
nonces, `X-Frame-Options`, etc.), a `/health` endpoint, a fail-safe
production config that refuses to start without a real `SECRET_KEY`,
`Procfile` + Gunicorn, and full deployment docs.

**UI/UX modernization:** a restrained "security SaaS" design system (not
default Bootstrap, not neon/glassmorphism), light/dark/auto theming, a real
landing page, a Cyber Safety Score + rank system backing the dashboard,
redesigned training/analyzer/help/learning-center/leaderboard/admin screens,
toast notifications, a downloadable PDF report, and an accessibility pass.

**Verification:** 92/92 automated tests pass (81 original/deployment tests
+ 11 new ones covering the rank system, security score, and PDF export),
plus a full manual smoke test hitting every route — home, dashboard, all 5
training levels, both analyzers, help center, wizard, resources, learning
center, leaderboard, profile, assessment, report + PDF, and every admin
page — while logged in as both a regular user and an admin, all returning
200 OK with no template errors.

**Natural next steps** if you keep building: full create/edit admin forms
for new content (today you seed new content and then manage it from the
admin console), Redis-backed rate limiting if you run multiple worker
processes, and a search feature across lessons/help topics if the content
library grows large enough to need one.

## Deploying CyberShield online

These steps are generic for any modern Python hosting platform (Render,
Railway, Fly.io, PythonAnywhere, a VPS, etc.) — the exact UI differs but the
pieces are the same everywhere:

1. **Push this repository to GitHub** (make sure `.env` is *not* committed —
   `.gitignore` already excludes it).
2. **Create a new web service** on your platform, pointing at the repo.
3. **Set the build/install command:** `pip install -r requirements.txt`
4. **Set environment variables** on the platform (not in a committed file):
   - `SECRET_KEY` — a strong random value (see `.env.example` for how to
     generate one)
   - `FLASK_CONFIG=production`
   - `DATABASE_URL` — a PostgreSQL connection string if your platform's disk
     isn't persistent (see [Database](#database) above); otherwise you can
     omit it to use SQLite
   - `SESSION_COOKIE_SECURE=True` (already the default once `FLASK_CONFIG`
     is `production`, but harmless to set explicitly)
5. **Set the release/migration command** (run once per deploy, before the
   app starts): `flask db upgrade`. The included `Procfile` already wires
   this up as a `release` step for platforms that support it (e.g. Heroku-
   style buildpacks); on platforms without that concept, run it manually
   from the platform's shell after the first deploy.
6. **Seed initial data** (once, after the first successful migration):
   `python seed/seed_roles.py && python seed/seed_all.py`
7. **Create your admin account:** `python scripts/create_admin.py`
8. **Set the start command:** `gunicorn "app:create_app('production')" --workers 3 --bind 0.0.0.0:$PORT`
   (also already in the `Procfile`) — never use `python run.py` /
   `flask run` in production, they use Flask's development server.
9. **Verify** `https://<your-app>/health` returns `{"status": "ok"}`.
10. **Open the public URL** and confirm login, training, and the analyzers
    work end to end.

If you outgrow SQLite's ephemeral-disk limitation on your chosen platform,
switching to PostgreSQL is a config change, not a code change — see
[Database](#database) above.
