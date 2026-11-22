"""Generate a bounded answer by selecting exact passages from authorized retrieval."""

import json
import os
from pathlib import Path

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from copilot.rag.pipeline import tokens

MODE = "grounded-source-selection"
PROMPT = Path(__file__).with_name("prompts") / "grounded-v3.md"
MAX_OUTPUT_TOKENS = 550
GENERIC = frozenset(
    {"a", "do", "for", "how", "i", "is", "me", "my", "on", "the", "to", "up", "what"}
)


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    chunk_id: str = Field(min_length=1, max_length=256)
    quote: str = Field(min_length=1, max_length=1500)


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    # Older provider adapters can still return the v2 answer field.
    answer: str = Field(default="", max_length=6000)
    abstained: bool
    citations: list[Citation] = Field(max_length=5)


def normalize(text):
    return " ".join(text.split())


def abstain(reason):
    answer = "I couldn’t verify an answer from the available sources."
    if reason in {"no_supporting_source", "model_abstained"}:
        answer += " I can help you raise a support ticket."
    return {
        "answer": answer,
        "citations": [],
        "abstained": True,
        "mode": MODE,
        "reason": reason,
        "prompt_version": PROMPT.stem,
    }


def select_passages(query, hits, client):
    anchors = set(tokens(query)) - GENERIC
    context = {
        hit.id: (hit, (hit.parent or hit.text)[:3600])
        for hit in hits
        if anchors
        & set(tokens(str(hit.metadata.get("title", "")) + " " + (hit.parent or hit.text)))
    }
    if not context:
        return abstain("no_supporting_source")
    sources = [
        {"chunk_id": key, "title": hit.metadata.get("title", ""), "content": passage}
        for key, (hit, passage) in context.items()
    ]
    try:
        response = client.complete(
            [
                {"role": "system", "content": PROMPT.read_text(encoding="utf-8")},
                {"role": "user", "content": json.dumps({"question": query, "sources": sources})},
            ]
        )
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return abstain("provider_error")
    try:
        selection = Selection.model_validate_json(response.text)
    except ValidationError:
        return abstain("invalid_model_output")
    if selection.abstained:
        return abstain("model_abstained" if not selection.citations else "invalid_model_output")
    citations, quotes = [], []
    for selected in selection.citations:
        if selected.chunk_id not in context:
            return abstain("unsupported_citation")
        hit, passage = context[selected.chunk_id]
        quote = normalize(selected.quote)
        if (
            not quote
            or quote not in normalize(passage)
            or not anchors & set(tokens(quote))
            or all(
                line.lstrip().startswith("#")
                for line in selected.quote.splitlines()
                if line.strip()
            )
        ):
            return abstain("unsupported_citation")
        if quote in quotes:
            return abstain("invalid_model_output")
        quotes.append(quote)
        citations.append(
            {
                "chunk_id": hit.id,
                "document_id": hit.document_id,
                "source": hit.source,
                "quote": quote,
            }
        )
    if not quotes or (
        "answer" in selection.model_fields_set
        and normalize(selection.answer) != normalize(" ".join(quotes))
    ):
        return abstain("unsupported_answer")
    return {
        "answer": "\n\n".join(quotes),
        "citations": citations,
        "abstained": False,
        "mode": MODE,
        "prompt_version": PROMPT.stem,
    }


class GroundedRag:
    mode = MODE

    def __init__(self, retriever, client):
        self.retriever = retriever
        self.client = client
        self.chunks = retriever.chunks

    def answer(self, query, **kwargs):
        return select_passages(query, self.retriever.search(query, **kwargs), self.client)


def configured_rag(data):
    from copilot.rag.service import VectorRag

    answer_mode = os.getenv("COPILOT_ANSWER_MODE", "extractive")
    if answer_mode not in {"extractive", "grounded"}:
        raise ValueError("COPILOT_ANSWER_MODE must be extractive or grounded")
    retriever = VectorRag.configured(data)
    if answer_mode == "extractive":
        return retriever

    from copilot.config import get_settings
    from copilot.llm.client import LUNA_MODEL, ModelClient

    settings = get_settings()
    if not settings.llm_model or settings.llm_model == "offline" or not settings.llm_api_key:
        raise ValueError("Grounded mode requires COPILOT_LLM_MODEL and COPILOT_LLM_API_KEY")
    client = ModelClient(
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key.get_secret_value(),
        timeout=settings.request_timeout_s,
        attempts=1,
        max_tokens=MAX_OUTPUT_TOKENS,
        json_response=settings.llm_model == LUNA_MODEL,
    )
    return GroundedRag(retriever, client)
