"""
url_checker.py
--------------
WHAT: A rule-based, text-only URL safety checker.
WHY:  Part C of the spec. Analyzes the URL STRING ONLY — never fetches,
      crawls, resolves DNS for, or otherwise visits the URL. That's a hard
      safety rule, not an optimization: the app must never auto-visit a
      possibly-malicious URL.
WHERE: app/services/url_checker.py — zero Flask/DB/network imports.
"""

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

DISCLAIMER = "This educational checker does not prove that a website is malicious or safe."

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

_IP_HOST_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

_KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "rebrand.ly", "cutt.ly", "shorturl.at",
}

_SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "confirm", "bank",
    "signin", "webscr", "kyc", "reward", "prize", "unlock", "billing",
]

# A short list of frequently-impersonated brand fragments, used only to
# flag look-alike patterns like "paypa1-secure.com" — this is NOT a claim
# that the real brand is involved, just a structural pattern check.
_COMMONLY_SPOOFED_BRAND_FRAGMENTS = [
    "paypal", "amazon", "google", "microsoft", "apple", "netflix",
    "bankofamerica", "hdfcbank", "icicibank", "sbi", "facebook", "instagram",
]


@dataclass
class UrlAnalyzerResult:
    risk_level: str
    score: int
    indicators: list = field(default_factory=list)
    explanation: str = ""
    recommended_action: str = ""
    disclaimer: str = DISCLAIMER
    technical: dict = field(default_factory=dict)


def analyze_url(raw_url: str) -> UrlAnalyzerResult:
    raw_url = (raw_url or "").strip()
    if not raw_url:
        return UrlAnalyzerResult(
            risk_level=RISK_LOW, score=0, indicators=[],
            explanation="No URL was provided to analyze.",
            recommended_action="Paste the URL above and try again.",
        )

    indicators = []
    score = 0

    # Normalize: if there's no scheme, urlparse mis-parses; add one for analysis only.
    parse_target = raw_url if "://" in raw_url else f"http://{raw_url}"
    parsed = urlparse(parse_target)
    host = parsed.hostname or ""
    path = parsed.path or ""
    port = parsed.port

    uses_https = raw_url.lower().startswith("https://")
    if not uses_https:
        indicators.append("Not using HTTPS")
        score += 1

    if _IP_HOST_RE.match(host):
        indicators.append("Uses a raw IP address instead of a domain name")
        score += 3

    if port and port not in (80, 443):
        indicators.append(f"Uses an unusual port ({port})")
        score += 2

    subdomain_count = max(host.count("."), 0)
    if host and not _IP_HOST_RE.match(host) and subdomain_count >= 3:
        indicators.append("Excessive number of subdomains")
        score += 2

    lowered_full = raw_url.lower()
    matched_keywords = [kw for kw in _SUSPICIOUS_KEYWORDS if kw in lowered_full]
    if matched_keywords:
        indicators.append(f"Suspicious keyword(s) in URL: {', '.join(sorted(set(matched_keywords)))}")
        score += min(3, len(set(matched_keywords)))

    if host in _KNOWN_SHORTENERS:
        indicators.append("Known URL-shortening service (destination is hidden)")
        score += 2

    if len(raw_url) > 90:
        indicators.append("Unusually long URL")
        score += 1

    if "@" in raw_url.split("://")[-1]:
        indicators.append("Contains '@' before the host — the real destination may be hidden")
        score += 3

    if "%" in raw_url and re.search(r"%[0-9A-Fa-f]{2}", raw_url):
        indicators.append("Contains encoded characters, which can hide the real destination")
        score += 1

    look_alike = _detect_lookalike_brand(host)
    if look_alike:
        indicators.append(f"Domain structurally resembles '{look_alike}' but is not that domain")
        score += 3

    if re.search(r"\.(zip|exe|scr|apk)(\?|$)", path, re.I):
        indicators.append("Path points to a directly downloadable executable/archive file")
        score += 2

    if score == 0:
        risk = RISK_LOW
    elif score <= 3:
        risk = RISK_LOW
    elif score <= 6:
        risk = RISK_MEDIUM
    else:
        risk = RISK_HIGH

    return UrlAnalyzerResult(
        risk_level=risk,
        score=score,
        indicators=indicators,
        explanation=_build_explanation(indicators),
        recommended_action=_build_recommendation(risk),
        technical={
            "protocol": "https" if uses_https else ("http" if "://" in raw_url else "(none specified)"),
            "domain": host or "(could not be parsed)",
            "port": port if port else ("443 (default)" if uses_https else "80 (default)"),
            "path": path or "/",
            "subdomain_count": subdomain_count,
        },
    )


def _detect_lookalike_brand(host: str):
    """Very simple structural check: brand name present but NOT as the
    actual registrable domain (e.g. 'paypal-secure-login.com' or
    'paypa1.com'), which is a classic typosquatting/impersonation pattern."""
    if not host:
        return None
    host_no_tld = re.sub(r"\.(com|net|org|in|co|info|xyz|top|online)$", "", host, flags=re.I)
    for brand in _COMMONLY_SPOOFED_BRAND_FRAGMENTS:
        if brand in host_no_tld and host_no_tld != brand:
            return brand
        # crude leetspeak substitution check: o->0, l->1, i->1
        leet = brand.replace("o", "0").replace("l", "1").replace("i", "1")
        if leet != brand and leet in host_no_tld:
            return brand
    return None


def _build_explanation(indicators: list) -> str:
    if not indicators:
        return "No characteristics commonly associated with suspicious links were detected."
    joined = "; ".join(indicators)
    return f"This URL contains {len(indicators)} characteristic(s) commonly associated with suspicious links: {joined}."


def _build_recommendation(risk: str) -> str:
    if risk == RISK_HIGH:
        return (
            "Do not visit this link or enter any information. If it claims to be from an "
            "organization you use, go directly to their official website or app instead of "
            "clicking this link."
        )
    if risk == RISK_MEDIUM:
        return "Be cautious. Avoid entering credentials or personal information via this link."
    return "No strong warning signs were detected, but always double-check the domain before entering any information."
