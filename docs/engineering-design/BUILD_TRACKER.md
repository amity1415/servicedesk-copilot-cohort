# Progressive build tracker

Use with [the engineering design](DESIGN.md). Milestones begin **planned** until implementation evidence is recorded. Existing reference code and historic test results are starting evidence, not a completed milestone or a validated deployment.

| ID | Milestone | Status | Branch or commit | Jenkins build or local evidence | Next action |
| --- | --- | --- | --- | --- | --- |
| M00 | Git and reproducible baseline | In progress | Local main and session tags 01–08 | Fresh session-08 checkout: 45 tests and benchmark passed | Configure GitHub remote and dependency lock workflow |
| M01 | Ingestion and trusted metadata | Complete | cohort-session-06 through 08 | reports/baselines/rag-batch-verification.json; 150 documents, 0 skips, unchanged repeat | Retain checks when adding persistent indexing |
| M02 | Persistent versioned index | Planned | — | — | Design migrations, exact search and generation activation |
| M03 | Authorized hybrid retrieval | Planned | — | — | Freeze retrieval subset and compare sparse/dense/fusion |
| M04 | Grounded service integration | In progress | Local RAG batch 05–08 | Shared VectorRag factory, authenticated HTTP and cumulative API/MCP tests | Validate live generation and provider errors |
| M05 | Reviewed evaluation gates | Planned | — | — | Review labels/splits and define claim-support checks |
| M06 | Durable observability | Planned | — | — | Trace one full request before adding dashboards |
| M07 | Jenkins CI and trusted quality jobs | Planned | — | — | Register the Windows agent and review the seed Jenkinsfile |
| M08 | Immutable staged deployment | Planned | — | — | Verify Docker agent and target-platform build/scan |
| M09 | Promotion and recovery | Planned | — | — | Rehearse compatible image/index rollback and data restore |

Allowed statuses: Planned, In progress, Blocked, Ready for review, Complete. Use Complete only after the milestone's acceptance evidence is attached. A blocked item should name the concrete missing input or failing dependency and preserve useful independent work.

## Milestone checklist

### M00 Git and reproducible baseline

- [ ] Review `.gitignore`, synthetic assets, secrets and uncurated reports before staging.
- [ ] Establish local Git history and choose a real remote without embedding credentials.
- [ ] Check a fresh clone contains every dependency of the running application and tests.
- [ ] Choose target Python and implement/validate the dependency-lock workflow.
- [ ] Record exact baseline commit, environment, tests and known failing quality target.

### M01 Ingestion and trusted metadata

- [x] Normalize metadata across Markdown, HTML, PDF and DOCX.
- [x] Join current/superseded policy revisions to the authoritative register.
- [x] Strip HTML portal chrome and preserve tables and ordered steps.
- [x] Enforce missing-audience denial and IT-only runbook visibility.
- [x] Include metadata/parser/chunker changes in invalidation; quarantine bad sources.

### M02 Persistent versioned index

- [ ] Review migrations, keys, vector dimension and scoped database permissions.
- [ ] Build an exact-search reference and measure representative authorized subsets.
- [ ] Create candidate generations, validate them and atomically activate a generation.
- [ ] Test unchanged ingestion, changed source replacement and source withdrawal.
- [ ] Prove rollback cannot reintroduce withdrawn or newly restricted content.

### M03 Authorized hybrid retrieval

- [ ] Share visibility/version predicates across dense and sparse queries.
- [ ] Measure code/ID, OS, region, role and conversational follow-up subsets.
- [ ] Fuse/deduplicate/rerank only authorized candidates.
- [ ] Compare quality and latency with the prior frozen baseline.
- [ ] Evaluate HNSW filtered recall if approximate indexing is introduced.

### M04 Grounded service integration

- [ ] Inject the selected RagService through both API and documents MCP.
- [ ] Centralize validated configuration and require explicit backend identity.
- [ ] Configure an authorized provider/revision and cost budget for live tests.
- [ ] Validate cited evidence, supported instructions, abstention and provider-error semantics.
- [ ] Retain offline reference mode without disguising it as live model output.

### M05 Reviewed evaluation gates

- [ ] Review RAG and agent expectations; preserve provenance and frozen splits.
- [ ] Implement split-aware evaluation and inspect template-family leakage.
- [ ] Add claim-support/context labels and independent human judge calibration.
- [ ] Require real end-state and forbidden-effect checks for agent outcomes.
- [ ] Demonstrate a deliberate regression is rejected; leave unmeasured metrics unknown.

### M06 Durable observability

- [ ] Propagate/extract W3C context through actual MCP/A2A HTTP calls.
- [ ] Export sanitized logs, traces and bounded-cardinality metrics.
- [ ] Configure collector, backends, retention, sampling and operator access.
- [ ] Demonstrate one cross-service request and one fault in traces/dashboards.
- [ ] Test planted PII/secret handling; set cost only from usage and versioned prices.

### M07 Jenkins CI and trusted quality jobs

- [ ] Verify Jenkins version/plugins, dedicated agent label, PATH and workspace access.
- [ ] Review/promote the example to root `Jenkinsfile` in a branch.
- [ ] Configure SCM branch discovery and a first manual clean-checkout build.
- [ ] Publish JUnit/contract reports; demonstrate failing and passing commits.
- [ ] Keep deployment/model secrets out of untrusted branch/PR builds.
- [ ] Add isolated Docker integration and budgeted trusted live-evaluation jobs.

### M08 Immutable staged deployment

- [ ] Verify Linux Docker agent, target-platform lock and pinned model assets.
- [ ] Build once, scan and record image digests plus SBOM/evidence.
- [ ] Review private networks, secrets, persistent state and liveness/readiness checks.
- [ ] Run staged six-scenario, security, telemetry and load gates.
- [ ] Record full compatible code/schema/index/model/prompt/policy release identity.

### M09 Promotion and recovery

- [ ] Promote the same tested digests through an authorized trusted release job.
- [ ] Rehearse previous-compatible-image and index-generation rollback.
- [ ] Verify withdrawals/visibility and business side effects after rollback.
- [ ] Restore a backup into an isolated environment and measure recovery time/loss.
- [ ] Define accepted RPO/RTO, retention, operator ownership and runbook.

## Evidence record template

Copy this for the milestone being implemented; keep historical evidence rather than overwriting a failed run with a success claim.

```text
Milestone and problem
Status and date
Owner and reviewer
Branch and exact commit
Changed files and contracts
Data source manifest and reviewed evaluation revision
Model index prompt policy and dependency identity
Commands or Jenkins job/build URL
Observed measurements and report locations
Deliberate failing case and observed rejection
Corrective change and regression evidence
Remaining blocker or limitation
Compatibility and rollback action
Next concrete increment
```
