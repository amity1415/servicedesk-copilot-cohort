"""Pinned CPU ONNX sentence encoder with normalized mean pooling and SQLite cache.

Weights download only through prepare_model(), not while serving a request.
No remote inference, API key or trust_remote_code is used.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

MODEL_REPO = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_FILES = ["tokenizer.json", "config.json", "onnx/model_quint8_avx2.onnx"]


def model_directory():
    return Path(os.getenv("COPILOT_LOCAL_MODEL_DIR", ".work/models/minilm"))


def prepare_model(directory=None, pin_file=None):
    from huggingface_hub import HfApi, hf_hub_download

    destination = Path(directory or model_directory())
    destination.mkdir(parents=True, exist_ok=True)
    pin_file = pin_file or Path(__file__).resolve().parents[3] / "policies/semantic_model.json"
    pin = json.loads(pin_file.read_text()) if pin_file.exists() else None
    repository = pin["repository"] if pin else MODEL_REPO
    revision = pin["revision"] if pin else HfApi(token=False).model_info(repository).sha
    checksums = {}
    for filename in MODEL_FILES:
        downloaded = hf_hub_download(
            repository, filename, revision=revision, cache_dir=str(destination / "hub"), token=False
        )
        target = destination / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(downloaded, target)
        checksums[filename] = hashlib.sha256(target.read_bytes()).hexdigest()
        if pin and checksums[filename] != pin["files"][filename]:
            raise ValueError("downloaded artifact does not match approved model pin")
    manifest = {
        "pooling": "attention-mask mean then L2 normalization",
        "max_tokens": 256,
        "dimension": 384,
        **(pin or {}),
        "repository": repository,
        "revision": revision,
        "files": checksums,
        "provider": "CPUExecutionProvider",
    }
    (destination / "MODEL_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def load_onnx_model(destination):
    import onnxruntime as ort
    from tokenizers import Tokenizer

    manifest_file = destination / "MODEL_MANIFEST.json"
    if not manifest_file.exists():
        raise RuntimeError(f"Local ONNX model manifest is missing at {manifest_file}")
    manifest = json.loads(manifest_file.read_text())
    for filename, expected in manifest["files"].items():
        actual = hashlib.sha256((destination / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"model artifact checksum mismatch: {filename}")
    tokenizer = Tokenizer.from_file(str(destination / "tokenizer.json"))
    tokenizer.enable_truncation(max_length=manifest["max_tokens"])
    tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        str(destination / "onnx/model_quint8_avx2.onnx"),
        options,
        providers=["CPUExecutionProvider"],
    )
    return manifest, tokenizer, session


class OnnxEncoder:
    def __init__(self, directory=None, cache=None):
        destination = Path(directory or model_directory())
        self.manifest, self.tokenizer, self.session = load_onnx_model(destination)
        self.identity = hashlib.sha256(
            json.dumps(self.manifest, sort_keys=True).encode()
        ).hexdigest()
        self.cache = Path(cache or destination / "vectors.sqlite3")
        self.cache.parent.mkdir(parents=True, exist_ok=True)
        self.encoded_misses = 0
        with closing(sqlite3.connect(self.cache)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS vectors (key TEXT PRIMARY KEY, value BLOB)")

    def encode(self, texts):
        import numpy as np

        keys = [
            hashlib.sha256((self.identity + "\0" + text).encode()).hexdigest() for text in texts
        ]
        found = {}
        with closing(sqlite3.connect(self.cache)) as db, db:
            for key in set(keys):
                row = db.execute("SELECT value FROM vectors WHERE key=?", (key,)).fetchone()
                if row:
                    found[key] = np.frombuffer(row[0], dtype=np.float32).copy()
            missing = {key: text for key, text in zip(keys, texts, strict=True) if key not in found}
            pairs = list(missing.items())
            for start in range(0, len(pairs), 16):
                batch = pairs[start : start + 16]
                encoded = self.tokenizer.encode_batch([text for _, text in batch])
                arrays = {
                    "input_ids": np.asarray([e.ids for e in encoded], dtype=np.int64),
                    "attention_mask": np.asarray(
                        [e.attention_mask for e in encoded], dtype=np.int64
                    ),
                    "token_type_ids": np.asarray([e.type_ids for e in encoded], dtype=np.int64),
                }
                feed = {item.name: arrays[item.name] for item in self.session.get_inputs()}
                output = self.session.run(None, feed)[0]
                if output.ndim != 3:
                    raise ValueError("expected token-level transformer output")
                mask = arrays["attention_mask"][..., None]
                pooled = (output * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1)
                pooled /= np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-12)
                for (key, _), vector in zip(batch, pooled, strict=True):
                    vector = vector.astype(np.float32)
                    found[key] = vector
                    db.execute(
                        "INSERT OR REPLACE INTO vectors VALUES (?,?)", (key, vector.tobytes())
                    )
                self.encoded_misses += len(batch)
        return [found[key].tolist() for key in keys]
