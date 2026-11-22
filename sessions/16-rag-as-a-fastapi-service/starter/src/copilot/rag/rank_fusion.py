"""Combine ranked chunk lists using reciprocal rank fusion."""

from copilot.rag.pipeline import Chunk


def reciprocal_rank_fusion(rankings: list[list[Chunk]], k: int = 5) -> list[Chunk]:
    scores, chunks = {}, {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, 1):
            scores[item.id] = scores.get(item.id, 0) + 1 / (60 + rank)
            chunks[item.id] = item
    return [chunks[key] for key in sorted(scores, key=scores.get, reverse=True)[:k]]
