# Evidence — session 16

- Both solution commands start Uvicorn on a fresh loopback port with temporary
  state, local TF-IDF retrieval, and extractive answers. Readiness showed 209
  indexed chunks. Administrator ingestion parsed all 150 documents with zero skips.
- Missing authentication returned `401`. A request over 8,000 characters
  returned `422` without echoing its question. Cross-employee thread access and
  employee ingestion returned `403`. A request ID appeared in the SSE response
  and API tests matched a response ID to the log. The simulated internal failure
  returned `500` with a fixed message.
- The Streamlit Mac response cited `KB-1017`. The Windows response and its
  follow-up cited `KB-1018`. Citations remained visible after rerunning each page.
- The untouched starter passed 52 inherited tests and failed its new test
  because the API module was absent. The solution implements that module and
  authenticates before calling the RAG pipeline.
- The gate matches both reports from `python scripts/session.py run 16` and
  `python -m copilot rag-http-verify`. It saves observed results, source revision,
  and test log digests in `verification/runtime-gate.json`. The two runs made
  zero paid calls.
