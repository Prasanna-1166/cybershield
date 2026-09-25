# CyberShield — Presentation Content (11 slides)

Copy each section into one slide. Speaker notes are included where useful.

---

## Slide 1 — Title
**CyberShield**
An Interactive Cybersecurity Awareness, Scam-Detection & Assistance Platform

*[Your name] · [Course/Project] · [Date]*

---

## Slide 2 — The Real-World Problem
- Phishing, smishing, vishing, fake KYC/bank alerts, impersonation, fake job
  offers, and payment scams are everywhere — including AI-assisted ones.
- **Problem 1:** People know scams exist in general but struggle to
  recognize a *specific realistic attempt* in the moment.
- **Problem 2:** When someone suspects a scam (or has already clicked/shared
  something), they usually don't know what to do next.

---

## Slide 3 — Motivation
- Most awareness tools are one-off quizzes: they build knowledge, not
  recognition skill against realistic, varied scenarios.
- Post-incident guidance is scattered across many sources, and reporting
  channels aren't obvious under stress.
- A single platform that trains recognition AND helps in the moment fills
  a real gap.

---

## Slide 4 — Proposed Solution
**CyberShield is not just a game.** It's a platform with three connected
layers, unified under one identity:

> "Learn to detect cyber threats before they trick you. Learn. Check. Respond."

---

## Slide 5 — PREVENT → DETECT → RESPOND
```
PREVENT → DETECT → RESPOND
   │          │         │
 Training   Message   Cyber Help Center
 Game       Analyzer  Incident Response Wizard
            URL       Official Reporting Resources
            Checker
```
- **Prevent:** 5-level gamified training (40 challenges)
- **Detect:** Message Analyzer + URL Safety Checker
- **Respond:** Help Center (12 scenarios) + Incident Wizard + Official Resources

---

## Slide 6 — System Architecture
- Flask app factory + Blueprints (main, auth, game, check, help, learn, admin)
- A dedicated **service layer** (scoring, badge rules, analyzers, wizard
  logic) kept independent of Flask/SQLAlchemy so core logic is directly
  unit-testable without a database.
- SQLAlchemy ORM → MySQL, via PyMySQL.
- Bootstrap + vanilla JS frontend, Chart.js for the report.

---

## Slide 7 — Major Modules
1. **Learn** — Gamified Training (5 levels, timer, hints, streaks, server-
   validated scoring, mandatory teaching on every wrong answer)
2. **Check** — Message Analyzer & URL Checker (rule-based, explainable,
   never certainty-claiming)
3. **Respond** — Cyber Help Center, Incident Response Wizard, Official Resources
4. **Measure** — Before/After Assessment, Personalized Cyber Safety Report
5. **Engage** — Dashboard, Leaderboard, 8 Badges
6. **Manage** — Admin Dashboard (users, content, analytics)

---

## Slide 8 — Technology Stack
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
- **Backend:** Python, Flask (Blueprints)
- **Database:** MySQL (SQLAlchemy + PyMySQL)
- **Charts:** Chart.js
- **Auth/Security:** Flask-Login, Flask-WTF (CSRF), Flask-Limiter (rate
  limiting), Werkzeug password hashing

---

## Slide 9 — Database & Security
- 15 tables: roles, users, levels, challenges, challenge_options, attempts,
  scores, badges, user_badges, learning_content, questions,
  question_options, assessment_attempts, reports, analyzer_history.
- Hashed passwords (PBKDF2-SHA256), parameterized queries throughout, CSRF
  on every form, rate-limited auth, role-based authorization on every
  protected route, no hard-coded secrets, friendly error pages.
- Analyzers never call external APIs and never store raw sensitive input.

---

## Slide 10 — Demo / Results
- Live demo flow suggestion: Register → Play Level 1 (see teaching
  feedback on a wrong answer) → Run the Message Analyzer on a sample scam
  → Open the Incident Wizard for "Money transferred" (shows URGENT +
  helpline) → View Dashboard/Report → Admin panel (as ADMIN role).
- 75 automated tests across 8 files; core logic (scoring, badges,
  analyzers, wizard) independently unit-tested with zero DB dependency.

---

## Slide 11 — Future Scope
- Versioned database migrations (Flask-Migrate)
- Full in-browser content authoring for admins
- Expanded/pluggable analyzer rule sets
- Multi-region official-resources content
- Production-grade rate limiting (Redis-backed)

---

## Slide 12 (optional) — Conclusion
CyberShield demonstrates a full PREVENT → DETECT → RESPOND cybersecurity
platform — not just a quiz — built with secure, modular, tested code from
the ground up.
