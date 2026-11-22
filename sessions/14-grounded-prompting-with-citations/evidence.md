# Evidence — session 14

Status: not yet completed by learner.

- Source revision and environment:
- Configuration, data and model identity:
- Commands executed:
- Observed results and report location:
- Required evidence: Requests 1 and 2 transcripts plus citation-membership tests and human entailment review
- Deliberate failure observed:
- Fix and regression check:
- Tradeoff and unresolved limitation:
- Integration gate passed or explicitly deferred:
- Reviewer:

## Instructor checkpoint, 22 November 2026

The live runner and completion checks were prepared on top of `5b75c67`.
The implementation remains pending live validation and human review.

| Check | Observed result |
| --- | --- |
| Standalone solution | 51 tests passed |
| Learner starter | 50 inherited tests passed. The new citation contract failed at the missing learner implementation as expected. |
| Integrated application | 123 tests passed with 18 dependency deprecation warnings. Ruff lint and format checks passed. |
| Standalone and integrated CLI fixtures | All three case outcomes matched after normalizing source paths. |
| Authenticated HTTP fixture | Grounded mode ready with TF–IDF retrieval and 209 chunks. Mac VPN cited KB-1017, Windows error 809 cited KB-1018, and unknown policy abstained with a support-ticket offer. |
| Existing workflow smoke test | A vague new-joiner request returned `needs_details`. |
| Provider guard rehearsal | The HTTP API sent both authorized cases through the guard with an offline upstream fixture. Checks covered GPT-6 Luna's standard tier, JSON mode and completion limit, along with request bounds, provider errors and review binding. |
| Paid calls | Zero |

The HTTP fixture report is `reports/integrated/rag/grounded-runtime.json`.
Its two model requests measured 6,434 and 2,807 bytes with the fixture model ID,
before the live runner's framing allowance. The unknown policy and workflow
smoke test used zero model requests.

The GPT-6 Luna request preview used the same API with a local provider adapter.
The Mac request contained passages from KB-1017, KB-1061, KB-1094 and the REF-003
glossary. The Windows request contained passages from KB-1018. Each passage
matched the corresponding chunk and its source file matched the synthetic
dataset manifest. The requests measured 6,529 and 2,902 bytes. The preview
forwarded no traffic to a provider.

## Full-application Docker check, 22 November 2026

Built the API, Streamlit, ticketing mock, three MCP services and HR partner
images and started them with PostgreSQL in an isolated, loopback-only Compose
project. The application used TF–IDF extractive retrieval. The API reported
209 chunks. Streamlit, ticketing and HR discovery returned HTTP 200. PostgreSQL
reported pgvector 0.8.7 and 300 seeded employees. The Windows environment and
the Linux API container passed `pip check`.

All six acceptance flows passed over real service connections. Mac and Windows
VPN cited their expected articles, including the Windows follow-up. Replayed
ticket creation reused the ticket ID. FinSight fulfilment was denied until both
approvals were recorded. HR onboarding completed five work items. The
privilege-change request was blocked.

Compose 2.10.2's `--wait` returned an error for the MCP service with an
intentionally disabled container health check. The HTTP tests exercised those
services through the API and passed.

## First live run, 22 November 2026

Both GPT-6 Luna requests returned HTTP 200 and used their full 400-token output
limit. The API rejected both replies with `invalid_model_output` and abstained.
The provider reported 1,523 and 637 input tokens. The conservative estimate
for both requests was $0.00067. The unknown policy and new-joiner checks
completed locally without provider calls.

The revised prompt returns excerpts and abstention status. The app builds the
display answer from verified quotations. Its live runner restricts each
question to the previously reviewed synthetic source IDs and records the
provider finish reason. With a 550-token output cap, a two-request retry
reserves $0.00230.

The revised prompt passed 123 integrated tests, 51 standalone tests, and
the authenticated API fixture with both expected VPN citations and the
unknown-policy abstention. Ruff lint, formatting and the diff check passed.

## Passing live retry, 22 November 2026

Both GPT-6 Luna responses finished with `stop`. The Mac VPN answer returned
five setup and connection steps from KB-1017, using 148 output tokens.
The Windows VPN 809 answer returned six resolution steps from KB-1018,
using 165 output tokens. The unknown policy abstained with no citations or
provider call. The new-joiner workflow returned `needs_details`.

The conservative cost estimate was $0.0004275 for the retry and $0.0010975
for both live runs combined. The transcript passed the runtime checks.
The human reviewer `amity1415` approved proceeding after the two answers and
their source links were presented. The review matches the live transcript hash
and both request IDs.

GitHub CLI authenticated as `amity1415`. The private cohort repository was
created with write access and added as `origin`. An authenticated Git lookup
confirmed it has zero refs. Session 15 follows the first verified push.
