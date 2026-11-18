"""Detection is defence in depth; action authorization remains authoritative."""

import re

ATTACK = re.compile(
    r"ignore\b.{0,60}\b(rules|instructions|previous)|make me an? admin|system prompt|"
    r"bypass.{0,30}approval|grant.{0,20}admin|reveal.{0,20}secret",
    re.I | re.S,
)


def suspicious(text: str) -> bool:
    return bool(ATTACK.search(text))


def mask(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "[EMAIL]", text)
    return re.sub(r"\bE\d{4}\b", "[EMPLOYEE]", text)


def valid_citations(citations: list[dict], retrieved: list) -> bool:
    allowed = {c.id for c in retrieved}
    return all(c.get("chunk_id") in allowed for c in citations)
