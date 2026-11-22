"""Pinned local cross-encoder for candidate reranking."""

import os
from pathlib import Path

from copilot.rag.semantic_encoder import load_onnx_model, prepare_model


def reranker_directory():
    return Path(os.getenv("COPILOT_LOCAL_RERANKER_DIR", ".work/models/reranker"))


def prepare_reranker():
    pin = Path(__file__).resolve().parents[3] / "policies/reranker_model.json"
    if not pin.is_file():
        raise FileNotFoundError(pin)
    return prepare_model(reranker_directory(), pin)


class OnnxReranker:
    def __init__(self):
        self.manifest, self.tokenizer, self.session = load_onnx_model(reranker_directory())

    def rank(self, query, chunks):
        import numpy as np

        scored = []
        for offset in range(0, len(chunks), 8):
            batch = chunks[offset : offset + 8]
            encoded = self.tokenizer.encode_batch([(query, chunk.text) for chunk in batch])
            arrays = {
                "input_ids": [item.ids for item in encoded],
                "attention_mask": [item.attention_mask for item in encoded],
                "token_type_ids": [item.type_ids for item in encoded],
            }
            feeds = {
                item.name: np.asarray(arrays[item.name], dtype=np.int64)
                for item in self.session.get_inputs()
            }
            scores = self.session.run(None, feeds)[0].reshape(-1)
            if not np.isfinite(scores).all():
                raise ValueError("reranker returned a non-finite score")
            scored.extend(zip(batch, scores, strict=True))
        return [chunk for chunk, _ in sorted(scored, key=lambda item: item[1], reverse=True)]
