"""
seed_data_badges.py
--------------------
WHAT: The 8 badge definitions. Keys must match app/services/badge_rules.py
      exactly, or the automatic-award logic won't find the row.
"""

BADGES = [
    {"key": "phishing_hunter", "name": "Phishing Hunter", "icon": "🎣",
     "description": "Completed Level 1 (Phishing Hunter) with 100% accuracy."},
    {"key": "url_detective", "name": "URL Detective", "icon": "🔍",
     "description": "Completed Level 2 (URL Detective) with 100% accuracy."},
    {"key": "password_protector", "name": "Password Protector", "icon": "🔐",
     "description": "Completed Level 3 (Account Guardian) with 100% accuracy."},
    {"key": "scam_spotter", "name": "Scam Spotter", "icon": "🕵️",
     "description": "Completed Level 4 (Scam Spotter) with 100% accuracy."},
    {"key": "fast_thinker", "name": "Fast Thinker", "icon": "⚡",
     "description": "Answered 5 or more challenges correctly within the fast-answer time bonus window."},
    {"key": "cyber_learner", "name": "Cyber Learner", "icon": "📚",
     "description": "Viewed 5 or more lessons in the Cyber Safety Learning Center."},
    {"key": "security_expert", "name": "Security Expert", "icon": "🛡️",
     "description": "Completed all 5 training levels."},
    {"key": "cybershield_champion", "name": "CyberShield Champion", "icon": "🏆",
     "description": "Earned every other badge — a true CyberShield champion."},
]
