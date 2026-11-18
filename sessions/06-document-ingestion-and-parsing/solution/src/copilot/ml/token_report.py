"""Named-tokenizer measurements; pricing is optional and never fabricated."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


def measure(
    data: Path,
    reports: Path,
    encoding=None,
    encoding_name="cl100k_base",
    input_price_per_million=None,
    output_price_per_million=None,
    assumed_output_tokens=128,
) -> dict:
    if assumed_output_tokens < 0:
        raise ValueError("output token assumption cannot be negative")
    if (input_price_per_million is None) != (output_price_per_million is None):
        raise ValueError("provide both input and output prices, or neither")
    if any(
        price is not None and price < 0
        for price in (input_price_per_million, output_price_per_million)
    ):
        raise ValueError("prices cannot be negative")
    if encoding is None:
        import tiktoken

        encoding = tiktoken.get_encoding(encoding_name)
    rows = [
        json.loads(line)
        for line in (data / "tickets/historical_tickets.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    ticket_counts = [
        len(encoding.encode(row["short_description"] + " " + row["description"])) for row in rows
    ]
    articles = [
        {"source": p.name, "tokens": len(encoding.encode(p.read_text(encoding="utf-8")))}
        for p in sorted((data / "kb").glob("*"))
        if p.suffix in {".md", ".html"}
    ]

    def distribution(values):
        ordered = sorted(values)
        return {
            "count": len(values),
            "mean": mean(values) if values else 0,
            "min": min(values, default=0),
            "max": max(values, default=0),
            "p95": ordered[min(len(ordered) - 1, int(0.95 * len(ordered)))] if ordered else 0,
        }

    cost = None
    if input_price_per_million is not None:
        cost = {
            "input_price_per_million": input_price_per_million,
            "output_price_per_million": output_price_per_million,
            "assumed_output_tokens_per_ticket": assumed_output_tokens,
            "estimated_request_text_input_total": sum(ticket_counts)
            * input_price_per_million
            / 1_000_000,
            "estimated_assumed_output_total": len(rows)
            * assumed_output_tokens
            * output_price_per_million
            / 1_000_000,
            "pricing_source": "caller supplied; not a fetched vendor price",
        }
    examples = {}
    for text in ("VPN error 809", "KB-1018", "LID-MFA-102", "0x80070005"):
        ids = encoding.encode(text)
        examples[text] = {"token_ids": ids, "pieces": [encoding.decode([i]) for i in ids]}
    report = {
        "encoding": encoding_name,
        "encoding_is_model_identity": False,
        "input_basis": (
            "request text only; excludes system prompt, retrieved context and chat framing"
        ),
        "article_basis": (
            "raw exported Markdown/HTML including "
            "metadata and portal markup, not cleaned RAG context"
        ),
        "tickets": distribution(ticket_counts),
        "articles": distribution([row["tokens"] for row in articles]),
        "article_counts": articles,
        "identifier_examples": examples,
        "cost_estimate": cost,
        "cost_status": "not measured; model prices not supplied"
        if cost is None
        else "forecast only, not billed provider usage",
    }
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "tokens.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
