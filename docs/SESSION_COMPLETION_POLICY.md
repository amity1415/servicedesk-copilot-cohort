# Session completion and commit policy

Confirmed on 18 November 2026: a source tree existing is not a completed session.

Before advancing from session N:

1. Implement the learner starter and cumulative solution contracts.
2. Execute the session solution against the actual training data.
3. Execute the corresponding feature through the integrated application's source,
   independently of the session launcher.
4. Pass the accumulated session acceptance tests and main regression checks.
   Start the integrated application from the updated workspace, or restart its
   affected local services if they are already running. Check readiness, then
   exercise the new capability through its normal application entry point.
   Verify an existing workflow through the running app as a smoke test.
   For a CLI-only capability, run its integrated CLI command and check any
   affected services.
5. Inspect real output artifacts and confirm required metadata, split and scope.
6. Complete required live/service checks. A mock, preflight or unknown result does
   not certify a required live capability.
7. Save evidence, review the scoped diff, and commit the verified implementation.
   Record the running-app configuration, startup or restart, readiness, the
   feature and smoke-test inputs, and observed results. Keep credentials out of
   the evidence. Leave the session pending if a required runtime check cannot run.
8. Record that commit as the session completion pointer. For Session 14 onward,
   push the verified implementation and completion pointer to the agreed private
   GitHub repository and confirm they are on the remote branch before beginning N+1.

`scripts/complete_session.py N` enforces the currently defined runtime gates and
previous-session commit dependency. It stops on any failure and makes no paid
calls. Live-gated sessions remain pending until their required live evidence and
reviews exist. Each new session requires its own gate definition. Undefined
later gates fail closed.

Session 14 uses the [bounded live runner](../sessions/14-grounded-prompting-with-citations/README.md#live-acceptance)
to produce a transcript and a human review template. Supply both with
`--live-report` and `--human-review` when running the completion command.
The command validates reviewed evidence and reruns the offline checks.

Session 15 supplies a [review candidate](../evals/rag_session15_candidate.jsonl)
for the frozen cases. Run the completion command with `--evaluation-dataset`
pointing to the reviewed copy in `evals/`. Both pipeline measurements must
match across the standalone and integrated commands before the gate commits
the reviewed data and results.

The `status` field in `sessions/implementation_manifest.json` describes source
availability. The separate `completion_state` describes audited completion:
`pending_verification`, `verification_failed`, `verified_awaiting_commit`,
`verified_committed` or an explicit pending live requirement. Only
`verified_committed`, with a real commit and evidence, permits advancement.

Earlier cohort tags preserve historical source checkpoints. They are not rewritten
to pretend these stricter runtime checks occurred before the policy was adopted.
Current completion evidence and commit pointers provide the audit trail.

The runtime gate for session 3 reports a declared unit-rate cost forecast and its
assumptions, not billed provider usage or validation that a deployment model is
available. Refresh pricing/model decisions before live work. All unrelated live,
security and production release gates remain required by the program's build plan.


## Instructor authorized RAG batch exception

On 18 November 2026 the instructor explicitly requested implementation through
session 8 before validation. Sessions 5–8 are therefore one authorized batch:
implement all four, run their cumulative acceptance and starter checks, run the
corresponding main application features and actual semantic/HTTP checks, then
record verified per-session commits and checkpoint tags. This exception does not
mark session 4's live-model gate complete or authorize an unvalidated later batch.
The batch validator is `scripts/validate_rag_batch.py`; the original sequential
gate remains fail-closed for sessions without an authorized batch definition.
