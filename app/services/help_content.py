"""
help_content.py
----------------
WHAT: The content for all 12 Cyber Help Center scenario pages (Part D).
      Data-driven on purpose: one template (help/scenario.html) renders
      whichever scenario key is requested, so every scenario gets its own
      URL and real content without 12 near-duplicate template files.
WHERE: app/services/help_content.py
"""

OFFICIAL_RESOURCES_NOTE = (
    "Official procedures and contact information may change. Use the official "
    "government resource for the latest instructions."
)

SCENARIOS = {
    "suspicious-message": {
        "title": "I received a suspicious message",
        "what_happened": "You received a message (email, SMS, or chat) that shows signs of phishing or a scam — urgency, requests for information, or a suspicious link.",
        "immediate_steps": [
            "Don't click any links or download any attachments.",
            "Don't reply to the message.",
            "Run the text through the Message Analyzer for a second opinion.",
        ],
        "what_not_to_do": [
            "Don't call any phone number provided in the message.",
            "Don't forward it to others without warning them it may be a scam.",
        ],
        "account_safety_steps": [
            "If the message referenced a real account of yours, log in directly via the official app or website (not via the message) and check for unusual activity.",
        ],
        "when_to_contact_org": "If the message claims to be from a company or bank you use, contact them directly using the number on their official website or the back of your card — never a number from the message.",
        "when_to_report": "If the message asked for money, credentials, or personal information, consider reporting it (see Official Resources below).",
    },
    "clicked-link": {
        "title": "I clicked a suspicious link",
        "what_happened": "You clicked a link that may lead to a fake login page, a scam page, or a page that tries to install something on your device.",
        "immediate_steps": [
            "Close the page/tab immediately without entering any information.",
            "Do not download or run anything the page prompted you to.",
            "Run the link through the URL Safety Checker to see what it flags.",
        ],
        "what_not_to_do": [
            "Don't enter your password or OTP on the page, even if it looks familiar.",
            "Don't ignore it just because 'nothing seemed to happen'.",
        ],
        "account_safety_steps": [
            "If you're not sure whether you entered anything, change the password of any account the page impersonated, from a device you trust.",
            "Run a security/antivirus scan on your device if you're on a computer.",
        ],
        "when_to_contact_org": "Contact the real organization if the fake page impersonated them, so they're aware of the scam.",
        "when_to_report": "If the site tried to collect credentials or payment details, it's worth reporting.",
    },
    "entered-credentials": {
        "title": "I entered credentials on a suspicious website",
        "what_happened": "You typed a username/password into a website that turned out to be (or might be) fake.",
        "immediate_steps": [
            "Immediately change that password on the REAL site — go there directly, not via any link.",
            "If you reused that password anywhere else, change it there too.",
            "Enable multi-factor authentication (MFA) on the real account if you haven't already.",
        ],
        "what_not_to_do": [
            "Don't wait \"to see if anything bad happens\" before changing the password.",
            "Don't reuse the compromised password with small tweaks (e.g. adding a \"1\").",
        ],
        "account_safety_steps": [
            "Check the account's recent login activity / active sessions and sign out of anything unrecognized.",
            "Check for changed recovery email/phone on the account.",
        ],
        "when_to_contact_org": "Contact the real organization's support to flag that a phishing page impersonated them.",
        "when_to_report": "Report the phishing site, especially if it impersonated a bank or government service.",
    },
    "shared-otp": {
        "title": "I shared an OTP",
        "what_happened": "You shared a one-time password/verification code with someone or something that wasn't the real, official service.",
        "immediate_steps": [
            "Immediately check the account the OTP was for, and log out of all sessions if possible.",
            "Change the password of that account right away.",
            "Contact the bank/service provider immediately if the OTP was for a financial transaction.",
        ],
        "what_not_to_do": [
            "Never share another OTP if asked again — legitimate organizations do not ask you to read out an OTP over a call or message.",
        ],
        "account_safety_steps": [
            "Review recent transactions or account changes for anything you didn't authorize.",
        ],
        "when_to_contact_org": "Contact your bank/service provider immediately — timing matters a lot for OTP-related fraud.",
        "when_to_report": "Report immediately if any unauthorized transaction occurred (see the 1930 helpline in Official Resources).",
    },
    "shared-sensitive-info": {
        "title": "I shared sensitive information",
        "what_happened": "You shared information such as an ID number, address, or account details with someone who may not have been legitimate.",
        "immediate_steps": [
            "Note exactly what was shared and when.",
            "Watch for follow-up scam attempts that reference what you shared (scammers often use it to sound more convincing).",
        ],
        "what_not_to_do": [
            "Don't provide additional information to 'verify' your identity to the same contact.",
        ],
        "account_safety_steps": [
            "If financial account numbers were shared, contact your bank to flag the account for monitoring.",
        ],
        "when_to_contact_org": "Contact any organization whose identifiers (like an ID number) were shared, if relevant to them.",
        "when_to_report": "Report if the information could enable identity theft or fraud.",
    },
    "lost-money": {
        "title": "I lost money in an online scam",
        "what_happened": "You transferred money or made a payment as part of what turned out to be, or might be, a scam.",
        "immediate_steps": [
            "Contact your bank or payment provider IMMEDIATELY to ask about reversing or freezing the transaction — speed matters a great deal here.",
            "Report to the official cyber-financial fraud helpline right away (see below).",
            "Save all evidence: messages, transaction IDs, screenshots.",
        ],
        "what_not_to_do": [
            "Don't send further money to try to 'recover' the lost amount — recovery scams are common.",
        ],
        "account_safety_steps": [
            "Secure the account(s) used to make the payment (change password, enable MFA).",
        ],
        "when_to_contact_org": "Contact your bank/payment provider first — before anything else — since reversal windows are short.",
        "when_to_report": "Report immediately via the official cybercrime portal and the 1930 helpline.",
        "urgent": True,
    },
    "account-compromised": {
        "title": "My account may be compromised",
        "what_happened": "You're seeing signs someone else has accessed one of your accounts — unfamiliar activity, logins, or messages you didn't send.",
        "immediate_steps": [
            "Change the password immediately, from a trusted device.",
            "Sign out of all other sessions/devices in the account's security settings.",
            "Enable MFA if it isn't already on.",
        ],
        "what_not_to_do": [
            "Don't ignore repeated 'new login' notifications hoping they'll stop.",
        ],
        "account_safety_steps": [
            "Review and remove any unfamiliar connected apps or devices.",
            "Check and correct any changed recovery email/phone number.",
        ],
        "when_to_contact_org": "Use the account provider's official account-recovery process if you've been locked out.",
        "when_to_report": "Report if the account was used to scam your contacts or access financial services.",
    },
    "social-media-compromised": {
        "title": "My social-media account may be compromised",
        "what_happened": "Someone else appears to be posting, messaging your contacts, or has changed settings on your social media account.",
        "immediate_steps": [
            "Try to log in and change your password immediately.",
            "Use the platform's official 'my account is compromised' / account recovery flow if you're locked out.",
            "Warn your contacts not to trust messages or links sent 'by you' recently.",
        ],
        "what_not_to_do": [
            "Don't click 'recover my account' links sent to you by someone else claiming to help — use the platform's own app/website.",
        ],
        "account_safety_steps": [
            "Review recent posts, messages, and account info for anything you didn't do.",
            "Enable MFA/login alerts.",
        ],
        "when_to_contact_org": "Use the platform's official support/help center.",
        "when_to_report": "Report if it's being used to scam your contacts (impersonation) or spread malicious links.",
    },
    "fake-bank-kyc": {
        "title": "I received a fake bank/KYC message",
        "what_happened": "You received a message claiming your bank account will be blocked unless you 'update your KYC' or verify your account via a link.",
        "immediate_steps": [
            "Do not click the link or call any number in the message.",
            "Log in to your bank account only via the official app or website you already use.",
            "Run the message through the Message Analyzer.",
        ],
        "what_not_to_do": [
            "Never share your card number, CVV, PIN, or OTP to 'complete KYC' — banks don't ask for these this way.",
        ],
        "account_safety_steps": [
            "If you already clicked/entered anything, follow the 'I entered credentials' or 'I shared an OTP' guidance above.",
        ],
        "when_to_contact_org": "Call your bank using the number on your card or their official website to confirm if KYC is actually needed.",
        "when_to_report": "Report the message, especially if it named a specific real or fictional bank convincingly.",
    },
    "fake-job-offer": {
        "title": "I received a fake job offer",
        "what_happened": "You received an unsolicited job offer that asks for money upfront, personal documents, or seems too good to be true.",
        "immediate_steps": [
            "Independently verify the company through its official website/careers page — don't rely on contact info given in the offer.",
            "Never pay any 'registration', 'training', or 'equipment' fee to receive a job.",
        ],
        "what_not_to_do": [
            "Don't share ID documents, bank details, or upfront payments based on a message/call alone.",
        ],
        "account_safety_steps": [
            "If you already shared documents, monitor your identity/financial accounts closely for misuse.",
        ],
        "when_to_contact_org": "Contact the real company directly (via their official site) to check if the offer is genuine.",
        "when_to_report": "Report if money was requested or paid.",
    },
    "impersonation": {
        "title": "I received an impersonation message",
        "what_happened": "Someone is pretending to be a person, company, or authority you know or trust (friend, boss, bank, government agency) to manipulate you.",
        "immediate_steps": [
            "Verify through a separate, known channel — call the real person/organization using a number you already have, not one from the message.",
            "Be especially cautious of urgent requests for money or gift cards 'from' someone you know.",
        ],
        "what_not_to_do": [
            "Don't act on the request just because the name/photo looks right — these are easy to fake.",
        ],
        "account_safety_steps": [
            "If it impersonated your own account, see 'My account may be compromised' above.",
        ],
        "when_to_contact_org": "Contact the real person or organization directly to confirm and warn them they're being impersonated.",
        "when_to_report": "Report impersonation attempts, especially ones involving requests for money.",
    },
    "report-cybercrime": {
        "title": "I need to report cybercrime",
        "what_happened": "You've decided to formally report a cyber incident.",
        "immediate_steps": [
            "Gather evidence first: screenshots, message text, transaction IDs, phone numbers, URLs, timestamps.",
            "Use the Incident Response Wizard if you want step-by-step help preparing what to report.",
            "Use the official government reporting channel — see below.",
        ],
        "what_not_to_do": [
            "Don't delete the evidence (messages, emails) even after you've reported it.",
        ],
        "account_safety_steps": [
            "Secure any accounts involved before or alongside filing your report.",
        ],
        "when_to_contact_org": "Contact any bank/company involved in parallel with reporting, especially for financial fraud.",
        "when_to_report": "As soon as you have the basic evidence gathered — don't wait.",
    },
}

SCENARIO_ORDER = [
    "suspicious-message", "clicked-link", "entered-credentials", "shared-otp",
    "shared-sensitive-info", "lost-money", "account-compromised",
    "social-media-compromised", "fake-bank-kyc", "fake-job-offer",
    "impersonation", "report-cybercrime",
]
