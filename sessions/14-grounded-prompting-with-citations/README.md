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
- [Versioned grounded prompt](../../src/copilot/rag/prompts/grounded-v2.md)

Run `scripts/session.py run 14` for the standalone contract fixture,
`copilot rag-grounded-verify` for the shared source fixture, and
`python scripts/verify_grounded_runtime.py` for the HTTP fixture.

After provider, model, and spend are authorized, configure
`COPILOT_ANSWER_MODE=grounded`, `COPILOT_LLM_MODEL`, and
`COPILOT_LLM_API_KEY` locally. Set `COPILOT_LLM_BASE_URL` when using
a different OpenAI-compatible endpoint. Restart the API and capture the
Mac VPN and Windows VPN 809 transcripts. Check that an unknown policy
abstains. Have a human reviewer compare each accepted excerpt with the
question and underlying source before recording completion.

## Deliberate failure exercise

Make the model cite an existing but irrelevant chunk; explain why membership validation alone misses this. Capture the failing behaviour first, then implement the fix and retain the regression check.

## Evidence and exit criteria

Requests 1 and 2 transcripts plus citation-membership tests and human entailment review. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
