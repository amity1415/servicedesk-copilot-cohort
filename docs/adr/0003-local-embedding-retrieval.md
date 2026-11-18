# ADR 0003 Local embedding retrieval

The shared app supports opt-in neural retrieval with
`COPILOT_RETRIEVAL_BACKEND=neural`. TF-IDF remains the default. Both modes apply
the same audience, OS, region, and exact error-code filters before scoring.
The API readiness response reports the active retrieval mode.

Use the pinned MiniLM L6 CPU ONNX model in the neural path. Model revision,
artifact hashes, pooling, normalization, and dimension identify the vector
space. Cache keys combine that identity and the content hash in SQLite.

In a deliberate failure exercise, forcing L12 to use L6's cache identity
returned the previously stored L6 vector without inference. Restoring the
L12 identity produced a cache miss and a different vector for the same text.

On the local Intel x64 CPU, MiniLM L6 and L12 each scored 0.85 Recall@5 on
the same 20 draft questions using 384-dimensional normalized vectors. In
the initial integrated run, L6 indexed in 18.51 seconds and averaged 11.90 ms
per cold query. L12 indexed in 31.17 seconds and averaged 17.00 ms. Each
model encoded 226 distinct inputs on the first pass and zero on the repeat.
Retain L6 for the opt-in path given equal measured recall and lower latency
in this run. The timings include local cache and inference overhead.

Five questions contained numeric error codes. Both models missed the same
expected articles on three of those questions, KB-1002, KB-1006, and KB-1095.
These draft results leave the retrieval quality release gate open.
