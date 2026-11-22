# Session 14: Grounded prompting with citations

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 13 is the starting point. This increment becomes part of the same application and is retained in session 15.

## Engineering objective

A citation that points to a retrieved chunk establishes provenance, not entailment. Validate IDs in code and inspect whether each factual claim is supported. Abstention is a valid task outcome.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Version the grounded prompt; delimit source data; require answer and citation JSON; validate each citation against retrieved IDs; reject malformed or unsupported output; test Mac VPN, Windows 809 and unknown policy.

## Reference implementation

- [Passage selection and validation](../../src/copilot/rag/grounded.py)
- [Versioned grounded prompt](../../src/copilot/rag/prompts/grounded-v3.md)

Run `scripts/session.py run 14` for the standalone contract fixture,
`copilot rag-grounded-verify` for the shared source fixture, and
`python scripts/verify_grounded_runtime.py` for the HTTP fixture.

## Live acceptance

Set `COPILOT_LLM_PROVIDER=openai`, `COPILOT_LLM_MODEL=gpt-6-luna`, and a scoped
`COPILOT_LLM_API_KEY` in the ignored local `.env`. The selected model uses
standard Chat Completions, JSON mode, and `reasoning_effort=none`. The
transcript records the model ID returned by the provider.
[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) and [OpenAI Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)

Run the bounded acceptance check from the repository root.

```powershell
.\.venv\Scripts\python.exe scripts/verify_grounded_live.py --live `
  --model gpt-6-luna --max-input-tokens 7000 `
  --max-spend-usd 0.003 --input-usd-per-million 0.125 `
  --output-usd-per-million 0.50
```

The runner starts an isolated authenticated API with TF–IDF retrieval and a
temporary SQLite store. It forwards at most one model request for each of the
two VPN questions, with at most 550 output tokens per request. It checks the
USD ceiling against the supplied rates before startup. The local input ceiling
uses request bytes plus a framing allowance. Using the published cache-write
rate for all input reserves $0.00230 for the two calls. The transcript records
the finish reason, reported token usage and the estimate at those conservative
rates.
[OpenAI pricing](https://developers.openai.com/api/docs/pricing)

The unknown policy must
abstain without a provider call. The new-joiner workflow must still ask for
details.

The runner prints the transcript and review-template paths in
`reports/integrated/rag/`. For both answers, the reviewer compares each
excerpt with the cited source and applicable platform or error code, then
records their name, verdicts, and notes in the review JSON. Leave its transcript
hash and request IDs intact. With both verdicts supported, run:

```powershell
.\.venv\Scripts\python.exe scripts/complete_session.py 14 `
  --live-report $session14Transcript --human-review $session14Review
```

The completion command checks that the review matches the transcript and the
transcript matches the current app and data. It reruns the standalone and
integrated fixture checks before committing the evidence.

## Deliberate failure exercise

Make the model cite an existing but irrelevant chunk; explain why membership validation alone misses this. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Requests 1 and 2 transcripts plus citation-membership tests and human entailment review. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
