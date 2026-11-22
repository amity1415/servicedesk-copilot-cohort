"""Paired evaluation of the course's two extractive RAG configurations."""

from __future__ import annotations

import hashlib
import random
import re
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import fmean
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from copilot.rag.loaders import fingerprint, is_allowed
from copilot.rag.query import rewrite
from copilot.rag.service import VectorRag

METRICS = ("recall_at_5", "context_precision", "faithfulness", "answer_relevance")
SPLITS = ("development", "heldout")
ACTION_SECTIONS = {"steps", "resolution", "response", "troubleshooting", "checklist", "key points"}
BOOTSTRAP_SAMPLES = 1000
BOOTSTRAP_SEED = 15


class Case(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_articles: list[str]
    reference_answer: str = Field(min_length=1)
    split: Literal["development", "heldout"]
    review_status: Literal["draft", "reviewed"]
    source_ticket: str | None = None
    os: str | None = None
    region: str | None = None
    reviewer: str | None = None
    reference_excerpts: dict[str, list[str]] = Field(default_factory=dict)


def dataset_path(data: Path) -> Path:
    fixture = Path(__file__).resolve().parents[3] / "fixtures/rag-evaluation"
    evals = data.parent / "evals"
    for path in (
        fixture / "golden-reviewed.jsonl",
        fixture / "golden.jsonl",
        evals / "rag_session15_reviewed.jsonl",
    ):
        if path.is_file():
            return path
    return evals / "rag_session15_candidate.jsonl"


def load_cases(raw: bytes) -> list[Case]:
    cases = [Case.model_validate_json(line) for line in raw.splitlines() if line.strip()]
    if not cases or len({case.id for case in cases}) != len(cases):
        raise ValueError("The evaluation dataset needs unique, nonempty case IDs")
    if any(len(set(case.expected_articles)) != len(case.expected_articles) for case in cases):
        raise ValueError("Expected article IDs must be unique within each case")
    return cases


def normalized(text: str) -> str:
    return " ".join(text.split())


def suggested_excerpts(text: str) -> list[str]:
    """Propose verbatim instructions from action sections for draft review."""
    excerpts = []
    for section in re.split(r"(?m)^#{1,6}\s+", text)[1:]:
        heading, _, body = section.partition("\n")
        if heading.strip().casefold() not in ACTION_SECTIONS:
            continue
        for line in body.splitlines():
            if line.strip():
                content = re.sub(r"^\s*(?:\d+\.\s+|[-*]\s+)", "", line)
                excerpts.append(normalized(content))
    return excerpts


def case_evidence(case: Case, documents: dict) -> tuple[dict[str, list[str]], list[str]]:
    expected = set(case.expected_articles)
    if unknown := expected - documents.keys():
        raise ValueError(f"{case.id}: expected article does not exist: {sorted(unknown)}")
    excluded = sorted(
        article
        for article in expected
        if not is_allowed(documents[article].metadata, os_name=case.os, region=case.region)
    )
    supplied = {
        article: [normalized(excerpt) for excerpt in excerpts]
        for article, excerpts in case.reference_excerpts.items()
    }
    for article, excerpts in supplied.items():
        if article not in expected or not excerpts:
            raise ValueError(f"{case.id}: excerpts need an expected source")
        text = normalized(documents[article].text)
        if any(not excerpt or excerpt not in text for excerpt in excerpts):
            raise ValueError(f"{case.id}: a reference excerpt is absent from {article}")
    if case.review_status == "reviewed":
        if not (case.reviewer or "").strip() or excluded or supplied.keys() != expected:
            raise ValueError(f"{case.id}: reviewed cases need applicable excerpts and a reviewer")
        return supplied, excluded
    suggested = {
        article: suggested_excerpts(documents[article].text) for article in case.expected_articles
    }
    return suggested | supplied, excluded


def score_case(case: Case, excerpts: dict, hits: list, answer: dict) -> dict:
    expected = set(case.expected_articles)
    ranked = hits[:5]
    retrieved = {hit.document_id for hit in ranked}
    complete_evidence = all(excerpts.get(article) for article in expected)
    contexts = {hit.id: normalized(hit.parent or hit.text) for hit in ranked}
    relevant = {
        hit.id
        for hit in ranked
        if any(excerpt in contexts[hit.id] for excerpt in excerpts.get(hit.document_id, ()))
    }
    ranked_by_id = {hit.id: hit for hit in ranked}
    claimed_sources = {row["chunk_id"]: row["document_id"] for row in answer.get("citations", ())}
    cited = {
        chunk_id
        for chunk_id, document_id in claimed_sources.items()
        if chunk_id in ranked_by_id and ranked_by_id[chunk_id].document_id == document_id
    }
    answer_text = normalized(answer["answer"])
    sentences = [normalized(line) for line in answer["answer"].splitlines() if line.strip()]
    abstained = answer["abstained"]
    faithfulness = None
    if not abstained:
        faithfulness = (
            fmean(any(line in contexts[chunk_id] for chunk_id in cited) for line in sentences)
            if sentences and cited == claimed_sources.keys()
            else 0.0
        )
    relevance = None
    if not expected:
        relevance = float(abstained)
    elif complete_evidence:
        relevant_articles = {
            ranked_by_id[chunk_id].document_id
            for chunk_id in cited & relevant
            if any(
                excerpt in answer_text and excerpt in contexts[chunk_id]
                for excerpt in excerpts[ranked_by_id[chunk_id].document_id]
            )
        }
        relevance = len(relevant_articles) / len(expected) if not abstained else 0.0

    failure = None
    if expected and not expected.intersection(retrieved):
        failure = "retrieval_miss"
    elif expected and complete_evidence and not relevant:
        failure = "bad_chunk"
    elif relevance == 0.0 or faithfulness is not None and faithfulness < 1.0:
        failure = "generation"
    return {
        "recall_at_5": len(expected & retrieved) / len(expected) if expected else None,
        "context_precision": len(relevant) / len(ranked) if ranked and complete_evidence else None,
        "faithfulness": faithfulness,
        "answer_relevance": relevance,
        "retrieved": [hit.document_id for hit in ranked],
        "relevant_chunks": sorted(relevant),
        "citations": sorted(claimed_sources.values()),
        "answer": answer["answer"],
        "abstained": abstained,
        "failure": failure,
    }


def bootstrap_delta(pairs: list[tuple[float, float]]) -> dict:
    if not pairs:
        return {"estimate": None, "ci95": None, "count": 0}
    deltas = [current - baseline for baseline, current in pairs]
    rng = random.Random(BOOTSTRAP_SEED)
    samples = sorted(fmean(rng.choices(deltas, k=len(deltas))) for _ in range(BOOTSTRAP_SAMPLES))
    last = len(samples) - 1
    return {
        "estimate": fmean(deltas),
        "ci95": [samples[int(0.025 * last)], samples[int(0.975 * last)]],
        "count": len(pairs),
    }


def summarize(rows: list[dict]) -> dict:
    result = {
        "count": len(rows),
        "answerable": sum(bool(row["expected_articles"]) for row in rows),
        "corpus_coverage": {
            side: sum(row[side]["contains_expected"] for row in rows)
            for side in ("baseline", "current")
        },
    }
    for metric in METRICS:
        scores = {
            side: [row[side][metric] for row in rows if row[side][metric] is not None]
            for side in ("baseline", "current")
        }
        pairs = [
            (row["baseline"][metric], row["current"][metric])
            for row in rows
            if row["baseline"][metric] is not None and row["current"][metric] is not None
        ]
        result[metric] = {
            side: {"mean": fmean(values) if values else None, "count": len(values)}
            for side, values in scores.items()
        }
        result[metric]["paired_delta"] = bootstrap_delta(pairs)
    return result


def pipeline_configuration(rag: VectorRag, corpus: str, rewrites: bool) -> dict:
    fingerprints = sorted(fingerprint(document) for document in rag.documents)
    return {
        "corpus": corpus,
        "corpus_sha256": hashlib.sha256("\n".join(fingerprints).encode()).hexdigest(),
        "documents": len(fingerprints),
        "chunks": len(rag.chunks),
        "chunking": rag.strategy,
        "query_rewrite": rewrites,
    }


def evaluate(data: Path, questions: Path) -> dict:
    raw = questions.read_bytes()
    cases = load_cases(raw)
    baseline = VectorRag.from_data(data, "fixed", baseline=True)
    current = VectorRag.from_data(data, "recursive")
    documents = {doc.id: doc for doc in current.documents if doc.id.startswith("KB-")}
    corpus_ids = {
        "baseline": {doc.id for doc in baseline.documents},
        "current": set(documents),
    }
    rows = []
    for case in cases:
        excerpts, excluded = case_evidence(case, documents)
        row = {
            **case.model_dump(),
            "reference_excerpts": excerpts,
            "scope_conflicts": excluded,
            "source_scope": {
                article: {
                    field: documents[article].metadata.get(field)
                    for field in ("title", "audience", "os", "region")
                }
                for article in case.expected_articles
            },
        }
        for name, rag, query in (
            ("baseline", baseline, case.question),
            ("current", current, rewrite(case.question)),
        ):
            scope = {"os_name": case.os, "region": case.region, "role": "employee"}
            hits = rag.search(query, **scope)
            row[name] = score_case(case, excerpts, hits, rag.answer(query, **scope))
            row[name]["contains_expected"] = bool(case.expected_articles) and (
                set(case.expected_articles) <= corpus_ids[name]
            )
        rows.append(row)

    failures = [
        {"id": row["id"], "split": row["split"], "side": side, "cause": row[side]["failure"]}
        for side in ("current", "baseline")
        for row in rows
        if row[side]["failure"]
    ][:10]
    split_sources = {
        split: {
            article for case in cases if case.split == split for article in case.expected_articles
        }
        for split in SPLITS
    }
    return {
        "mode": "local-extractive-rag-evaluation",
        "provider_calls": 0,
        "effective_date": date.today().isoformat(),
        "dataset": {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "case_count": len(cases),
            "unanswerable_count": sum(not case.expected_articles for case in cases),
            "review_status": dict(Counter(case.review_status for case in cases)),
            "scope_conflicts": sum(bool(row["scope_conflicts"]) for row in rows),
            "shared_articles_across_splits": sorted(
                split_sources["development"] & split_sources["heldout"]
            ),
        },
        "pipelines": {
            "baseline": pipeline_configuration(baseline, "session-05-fixture", False),
            "current": pipeline_configuration(current, "synthetic-data-pack", True),
        },
        "judge": {
            "method": "exact-evidence-extractive-v1",
            "recall_at_5": "Expected article coverage among the first five chunks",
            "context_precision": "Returned chunks containing a labelled source excerpt",
            "faithfulness": "Answer lines found verbatim in valid cited passages",
            "answer_relevance": "Expected article evidence in the answer or correct abstention",
            "bootstrap": {"samples": BOOTSTRAP_SAMPLES, "seed": BOOTSTRAP_SEED, "paired": True},
            "scope": "Extractive answers on the supplied case labels",
        },
        "splits": {
            split: summarize([row for row in rows if row["split"] == split]) for split in SPLITS
        },
        "failure_examples": failures,
        "cases": rows,
    }
