"""Fixed-window baseline. Later sessions introduce structural boundaries."""

import hashlib
import json


def make_chunks(document, strategy="fixed", size=1200, overlap=120, encoder=None, threshold=0.55):
    from copilot.rag.pipeline import Chunk

    if not 0 <= overlap < size:
        raise ValueError("invalid size/overlap")
    if strategy != "fixed":
        raise ValueError("This session implements fixed windows only")
    identity = hashlib.sha256(
        json.dumps(
            {
                "digest": document.digest,
                "metadata": document.metadata,
                "size": size,
                "overlap": overlap,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()[:16]
    return [
        Chunk(
            f"{document.id}:fixed:{identity}:{i}",
            document.id,
            document.text[start : start + size],
            dict(document.metadata),
            document.source,
        )
        for i, start in enumerate(range(0, len(document.text), size - overlap))
    ]
