"""
seed_data_questions.py
------------------------
WHAT: The Before/After Assessment question bank (Part H) — 12 questions
      (spec minimum is 10), covering phishing, URLs, passwords, scams, and
      general awareness.
"""

QUESTIONS = [
    {
        "category": "phishing",
        "text": "An email urgently asks you to click a link to 'verify your account' or it will be suspended. What should you do?",
        "explanation": "Legitimate organizations don't threaten immediate suspension via email links. Go to the official site/app directly instead.",
        "options": [
            ("Click the link right away to avoid losing access", False),
            ("Go to the organization's official website/app directly to check", True),
            ("Reply asking them to confirm it's real", False),
            ("Forward it to a friend to ask their opinion", False),
        ],
    },
    {
        "category": "phishing",
        "text": "What is a common warning sign of a phishing email?",
        "explanation": "Urgency and threats are one of the most common phishing tactics, designed to make you act before thinking.",
        "options": [
            ("It uses urgent, threatening language", True),
            ("It's addressed to you by name", False),
            ("It comes from a company you recognize", False),
            ("It has no attachments", False),
        ],
    },
    {
        "category": "url",
        "text": "Which of these URLs shows a classic look-alike/typosquatting pattern?",
        "explanation": "'arnaz0n' visually resembles a well-known brand using character substitution (rn for m, 0 for o) — a typosquatting technique.",
        "options": [
            ("https://www.wikipedia.org/wiki/Cybersecurity", False),
            ("https://arnaz0n-deals.com/prime/renew", True),
            ("https://docs.python.org/3/", False),
            ("https://www.mozilla.org/firefox/", False),
        ],
    },
    {
        "category": "url",
        "text": "A URL uses a raw IP address (like http://192.168.1.5/login) instead of a domain name. What does this suggest?",
        "explanation": "Legitimate services almost always use a proper registered domain name; a raw IP address is a common red flag for suspicious or malicious sites.",
        "options": [
            ("It's a red flag worth treating with caution", True),
            ("It's always completely safe", False),
            ("It means the site loads faster", False),
            ("It has no security implications", False),
        ],
    },
    {
        "category": "password",
        "text": "Which is the strongest password practice?",
        "explanation": "A unique password for every account limits the damage if any single service is breached.",
        "options": [
            ("Using the same strong password everywhere for consistency", False),
            ("Using a unique password for every account", True),
            ("Using your birthdate as part of every password", False),
            ("Writing all your passwords in a plain text file on your desktop", False),
        ],
    },
    {
        "category": "password",
        "text": "What does multi-factor authentication (MFA) protect against?",
        "explanation": "MFA adds a second proof of identity, so even a stolen password alone isn't enough for an attacker to log in.",
        "options": [
            ("It makes your password longer automatically", False),
            ("It prevents login even if your password alone is stolen", True),
            ("It replaces the need for a password entirely", False),
            ("It only works on mobile devices", False),
        ],
    },
    {
        "category": "password",
        "text": "Between a short complex password and a long random passphrase, which is generally stronger?",
        "explanation": "Length is one of the strongest factors in password security — long passphrases are generally harder to crack than short complex-looking passwords.",
        "options": [
            ("The short complex password, because of symbols", False),
            ("The long random passphrase, because of its length", True),
            ("They are always exactly equal in strength", False),
            ("Neither matters if you have antivirus software", False),
        ],
    },
    {
        "category": "scam",
        "text": "You receive an SMS saying you've won a prize for a contest you never entered. What is this most likely?",
        "explanation": "You can't win a contest you never entered — unsolicited prize claims are a very common scam lure.",
        "options": [
            ("A legitimate reward you should claim quickly", False),
            ("A likely scam — you never entered any contest", True),
            ("Something to forward to all your contacts", False),
            ("Proof your number was randomly selected legitimately", False),
        ],
    },
    {
        "category": "scam",
        "text": "A caller claiming to be bank 'fraud prevention' asks you to read out the OTP you just received. What should you do?",
        "explanation": "Banks never ask you to read out an OTP over a call — this is a direct OTP-theft attempt regardless of how urgent it sounds.",
        "options": [
            ("Read it out since they said it's urgent", False),
            ("Refuse and hang up — banks never ask for OTPs this way", True),
            ("Read out only half the OTP as a compromise", False),
            ("Ask them to call back later with the same request", False),
        ],
    },
    {
        "category": "scam",
        "text": "A message offers a job with 'immediate start' but asks for your bank details and ID copy before any interview. What is this?",
        "explanation": "No legitimate employer requests sensitive financial/ID information via unsolicited message before any interview process.",
        "options": [
            ("A normal part of modern hiring", False),
            ("Likely a job scam — legitimate employers don't ask this way", True),
            ("Something to comply with quickly to not miss the opportunity", False),
            ("Only risky if they also ask for a password", False),
        ],
    },
    {
        "category": "general",
        "text": "If you clicked a suspicious link but aren't sure whether you entered any information, what's the safest first step?",
        "explanation": "Changing the password for any account the fake page impersonated is the safest first step when in doubt.",
        "options": [
            ("Do nothing since you're not sure anything happened", False),
            ("Change the password of the impersonated account, just in case", True),
            ("Wait a week to see if anything unusual happens", False),
            ("Only worry about it if you get a strange call", False),
        ],
    },
    {
        "category": "general",
        "text": "Where should you report suspected cybercrime in India?",
        "explanation": "The National Cyber Crime Reporting Portal (cybercrime.gov.in) and the 1930 helpline are the official channels for reporting cybercrime in India.",
        "options": [
            ("Only by posting publicly on social media", False),
            ("The National Cyber Crime Reporting Portal / 1930 helpline", True),
            ("There's no official channel, just change your passwords", False),
            ("Only your personal email provider can help", False),
        ],
    },
]
