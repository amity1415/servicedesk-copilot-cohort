# Cumulative build and integration steps

Use one checkout throughout the course. The shipped code lives in `src/copilot`;
the separate `sessions` tree supplies teaching material and runnable experiments.
An experiment references shared source rather than copying a stale application
into forty folders. The provided repository contains the reference baseline;
learners implement the increments in their own branch. It does not include forty
historical Git snapshots.

1. Complete [setup](SETUP.md), run existing tests and inspect the six acceptance
   personas. Read the original [build plan](BUILD_PLAN.txt). Preserve its scope.
2. Work through sessions 01–04. Keep one train/test split across models, exclude
   resolution fields, record real token prices, add the mocked model tests and
   save the foundations ADR. Tag `v0.1-foundations` only after its gate passes.
3. Work through sessions 05–09. Keep Document and Chunk contracts stable across
   loaders and chunkers. Review the draft RAG labels. Fix ingestion metadata
   before comparing embedding models. Store model identity alongside vectors.
4. Integrate sessions 10–14. Start PostgreSQL, replace in-memory indexing with
   the database adapter, test updates and withdrawals, apply visibility before
   both rankings, add RRF and reranking, then validate citations and abstention.
   Preserve the Mac and Windows 809 scenarios as regressions.
5. In sessions 15–16, score 100 reviewed questions, save the four metrics and
   expose the measured pipeline through the authenticated API and UI. The shipped
   API currently selects the lexical reference; wiring the measured neural/PG
   pipeline into this factory is required before claiming `v0.2-rag`.
6. In sessions 17–20, run the ticket mock and build tools against real HTTP.
   Keep stable idempotency keys in durable state. Compare the bounded model loop
   with the workflow, then use `build_tool_graph` for separate decision/tool
   nodes and conditional routing. Prove PostgreSQL
   restart/resume before accepting the session 20 gate.
7. In sessions 21–25, integrate dependency planning, consented memory and support
   checks. Run faults and establish a persisted approval boundary. The offline
   FinSight reference enforces manager plus Finance owner approvals and licence
   capacity. Do not let a model, UI field or analyst role override those rules.
8. In sessions 26–28, compare actual specialist model runs with the baseline,
   add onboarding handoffs and evaluate all 25 attacks by forbidden effects.
   Pattern detection results are diagnostic coverage, not an attack-success score.
9. In sessions 29–32, start actual MCP servers and exercise tools, resources and
   prompts. Set `COPILOT_TRANSPORT=mcp` and the three server URLs, or use the
   application Compose overlay, which sets them. The cumulative test covers
   this path with in-process HTTP bridges. Complete fixed database SELECT-only
   tools and the full permission matrix before `v0.4-mcp`.
10. In session 33, start the separately owned HR A2A service, submit candidate
    `C-2041` with the fixture's explicit start date `2026-11-16`, and verify the
    returned task's candidate binding. The MCP onboarding tool connects HR
    completion to persisted simulated IT steps. The date is historical synthetic
    data; never interpret it as the next Monday at runtime. Verify the full flow
    in the deployment before marking its request 5 gate complete.
11. In sessions 34–37, snapshot schemas, benchmark the three boundaries, review
    40 agent tasks, hand-label 30 judge examples, and score actual end states and
    trajectories. Draft datasets are supplied to accelerate authoring and are
    explicitly unreviewed. Missing scores remain null.
12. In sessions 38–40, add the full-stack/nightly evaluations to CI, pin resolved
    model/index/prompt/policy identity, propagate traces across every boundary,
    scan images and dependencies, and run the six scenarios from a clean machine.
    The included Compose/UI/API reference is a starting environment, not a
    production-certified release. Tag `v1.0` only when actual evidence meets the
    release manifest targets.

At the end of every session, save `evidence.md`, review the diff, run the previous
checks and commit. Each module's gate is stricter than its individual offline
experiments. Consult [implementation status](IMPLEMENTATION_STATUS.md) for what
has actually been implemented and validated in this delivery.
