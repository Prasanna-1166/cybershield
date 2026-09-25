"""
seed_data_learning_content.py
-------------------------------
WHAT: All 14 Learning Center lessons named in the spec (Part G). Each has
      the What/Warning-signs/Example/What-to-do shape.
"""

LEARNING_CONTENT = [
    {
        "key": "phishing", "category": "phishing", "title": "Phishing",
        "what_is_it": "Phishing is when an attacker sends a fake message pretending to be a trusted organization or person, aiming to trick you into clicking a link, opening an attachment, or revealing information.",
        "warning_signs": "Urgent or threatening language\nGeneric greetings like 'Dear Customer'\nSuspicious sender domain\nRequests for passwords, OTPs, or personal info\nUnexpected attachments or links",
        "example": "An email claiming to be from your bank says your account will be suspended unless you 'verify' by clicking a link and entering your password.",
        "what_to_do": "Don't click links or reply. Go directly to the organization's official website or app to check your account.",
    },
    {
        "key": "smishing", "category": "phishing", "title": "Smishing (SMS Phishing)",
        "what_is_it": "Smishing is phishing carried out via SMS/text messages instead of email.",
        "warning_signs": "Unfamiliar short links\nUrgent account/delivery/payment claims\nRequests to 'update' or 'verify' via a link\nMessages from unknown or spoofed numbers",
        "example": "\"Your package couldn't be delivered. Pay a small fee here: [suspicious link]\" — for a package you never ordered.",
        "what_to_do": "Don't click links in unexpected texts. Verify directly with the sender/organization through official channels.",
    },
    {
        "key": "vishing", "category": "social_engineering", "title": "Vishing (Voice Phishing)",
        "what_is_it": "Vishing is phishing carried out over a phone call, where a scammer impersonates a trusted organization to extract information or push you to take an action.",
        "warning_signs": "Unsolicited call creating urgency or fear\nAsks you to read out an OTP or confirm sensitive details\nAsks you to install remote-access software\nRefuses to let you call back on an official number",
        "example": "A caller claims to be 'bank fraud prevention' and asks you to read out the OTP you just received to 'cancel' a suspicious transaction.",
        "what_to_do": "Hang up. Call the organization back using a number you already know is correct — never one provided by the caller.",
    },
    {
        "key": "social_engineering", "category": "social_engineering", "title": "Social Engineering",
        "what_is_it": "Social engineering is manipulating people (rather than hacking systems) into breaking normal security practices — through urgency, authority, fear, or trust.",
        "warning_signs": "Impersonation of authority (boss, bank, government)\nArtificial urgency or scarcity\nRequests that bypass normal procedure\nAppeals to fear, curiosity, or greed",
        "example": "An email 'from the CEO' urgently asks an employee to buy gift cards and send the codes, bypassing normal purchase approval.",
        "what_to_do": "Slow down and verify independently through a separate, known channel before acting on unusual requests.",
    },
    {
        "key": "suspicious_urls", "category": "urls", "title": "Suspicious URLs",
        "what_is_it": "A suspicious URL is a web address with structural characteristics commonly used to disguise a malicious or fake destination.",
        "warning_signs": "Raw IP address instead of a domain\nLook-alike/typosquatted domains\nExcessive subdomains or keyword stuffing\nURL shorteners hiding the real destination\n'@' symbols hiding the real host",
        "example": "http://novabank.com@account-verify-test.invalid — the real destination is 'account-verify-test.invalid', not novabank.com.",
        "what_to_do": "Check the actual domain carefully before clicking, or use the URL Safety Checker for a second opinion.",
    },
    {
        "key": "password_safety", "category": "passwords", "title": "Password Safety",
        "what_is_it": "Password safety means using strong, unique passwords for every account so a breach of one service doesn't compromise the rest.",
        "warning_signs": "Reusing the same password across multiple sites\nShort or common passwords ('password123')\nPasswords based on easily guessable personal info",
        "example": "Using \"Summer2024!\" for your email, bank, and shopping accounts means one breach exposes all three.",
        "what_to_do": "Use a unique, long password or passphrase for every account, ideally managed with a password manager.",
    },
    {
        "key": "mfa", "category": "passwords", "title": "Multi-Factor Authentication (MFA)",
        "what_is_it": "MFA requires a second proof of identity (like a code from an app) in addition to your password when logging in.",
        "warning_signs": "N/A — this is a protective measure, not a threat to watch for",
        "example": "Even if someone steals your password, MFA means they still can't log in without your phone's authenticator code.",
        "what_to_do": "Enable MFA on every account that offers it — especially email, banking, and social media.",
    },
    {
        "key": "account_security", "category": "accounts", "title": "Account Security",
        "what_is_it": "Account security covers the ongoing practices that keep your online accounts safe: strong passwords, MFA, and monitoring for unauthorized access.",
        "warning_signs": "Unfamiliar login notifications\nChanged recovery email/phone you didn't set\nUnrecognized active sessions or connected apps",
        "example": "You receive a 'new login from an unrecognized device' alert you didn't cause.",
        "what_to_do": "Change your password, sign out of other sessions, and enable MFA immediately.",
    },
    {
        "key": "impersonation", "category": "social_engineering", "title": "Impersonation",
        "what_is_it": "Impersonation is when someone pretends to be a person, company, or authority you trust in order to manipulate you.",
        "warning_signs": "Contact from a 'known' person on an unfamiliar channel/number\nRequests for money, gift cards, or sensitive info\nUrgency paired with unavailability to verify",
        "example": "\"Hi mom, I lost my phone, this is my new number, please send money urgently.\"",
        "what_to_do": "Verify through a separate, already-known channel before acting on the request.",
    },
    {
        "key": "online_scams", "category": "scams", "title": "Online Scams",
        "what_is_it": "Online scams are deceptive schemes conducted digitally to trick people out of money or information — prize scams, fake job offers, romance scams, and more.",
        "warning_signs": "Unsolicited offers that seem too good to be true\nRequests for upfront payment or fees\nPressure to act quickly, secretly, or without telling others",
        "example": "\"Congratulations! You've won a $500 voucher — claim it here\" for a contest you never entered.",
        "what_to_do": "If you didn't initiate it and it sounds too good to be true, treat it as a scam until proven otherwise.",
    },
    {
        "key": "payment_scams", "category": "scams", "title": "Payment Scams",
        "what_is_it": "Payment scams trick you into sending money, gift card codes, or payment details under a false pretext.",
        "warning_signs": "Requests for gift cards as payment\nUrgent, secretive payment requests\nFake invoices or 'customs fees' for unexpected packages",
        "example": "A message claims a small 'customs fee' is owed for a package you never ordered, with a payment link attached.",
        "what_to_do": "Never pay based on an unsolicited message. Verify independently before sending any money.",
    },
    {
        "key": "safe_browsing", "category": "browsing", "title": "Safe Browsing",
        "what_is_it": "Safe browsing habits reduce your exposure to malicious sites, downloads, and trackers while using the web.",
        "warning_signs": "Sites without HTTPS asking for sensitive info\nUnexpected download prompts\nPop-ups claiming urgent 'security' problems",
        "example": "A pop-up claims your device is infected and urges you to download a 'security tool' immediately.",
        "what_to_do": "Close suspicious pop-ups without clicking them, and only download software from official sources.",
    },
    {
        "key": "safe_messaging", "category": "messaging", "title": "Safe Messaging",
        "what_is_it": "Safe messaging habits help you avoid scams delivered through SMS, WhatsApp, and other chat apps.",
        "warning_signs": "Messages from unknown numbers claiming urgency\nLinks in unsolicited messages\nRequests to keep something 'secret' from others",
        "example": "An unknown number on WhatsApp claims to be a relative on a 'new number' and asks for money right away.",
        "what_to_do": "Verify identity through a known channel before trusting any request that arrives via chat.",
    },
    {
        "key": "basic_incident_response", "category": "incident_response", "title": "Basic Incident Response",
        "what_is_it": "Incident response is what you do after you suspect or confirm you've been targeted by a scam or attack — containing damage and recovering safely.",
        "warning_signs": "N/A — this is about the response process, not a threat to detect",
        "example": "You realize you entered your password on a fake site — the next steps matter as much as catching the phishing attempt itself.",
        "what_to_do": "Change affected passwords immediately, enable MFA, monitor accounts, and use the Cyber Help Center for step-by-step guidance.",
    },
]
