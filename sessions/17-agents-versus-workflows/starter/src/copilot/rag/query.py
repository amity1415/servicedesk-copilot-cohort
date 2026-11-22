"""Bounded, deterministic rewrite of a user's own retrieval follow-up."""

import re

IDENTIFIERS = re.compile(r"\b(?:[A-Z]{2,}-\d+(?:[._-]\w+)*|\d{3,})\b", re.IGNORECASE)
FOLLOW_UP = re.compile(r"\b(?:still|same problem|doesn['’]t work)\b", re.IGNORECASE)
ACRONYMS = {
    "MFA": "multi-factor authentication",
    "VPN": "virtual private network",
    "SSO": "single sign-on",
    "BYOD": "bring your own device",
}
ACRONYM_PATTERN = re.compile(r"\b(?:" + "|".join(ACRONYMS) + r")\b", re.IGNORECASE)
FOLLOW_UP_FILLER = frozenset(
    [
        "a",
        "am",
        "are",
        "does",
        "doesn",
        "have",
        "having",
        "i",
        "is",
        "it",
        "not",
        "problem",
        "same",
        "still",
        "t",
        "the",
        "this",
        "we",
        "work",
        "working",
    ]
)


def rewrite(query: str, previous: str = "") -> str:
    if previous and FOLLOW_UP.search(query) and not IDENTIFIERS.search(query):
        terms = set(re.findall(r"\b\w+\b", query.casefold()))
        query = f"{previous} {query}" if terms - FOLLOW_UP_FILLER else previous
    return ACRONYM_PATTERN.sub(
        lambda match: f"{ACRONYMS[match.group().upper()]} {match.group().upper()}", query
    )
