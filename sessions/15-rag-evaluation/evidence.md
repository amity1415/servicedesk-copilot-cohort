# Evidence — session 15

Status: not yet completed by learner.

- Source revision and environment:
- Configuration, data and model identity:
- Commands executed:
- Observed results and report location:
- Required evidence: Four-metric report with judge configuration, baseline, uncertainty and ten attributed failures
- Deliberate failure observed:
- Fix and regression check:
- Tradeoff and unresolved limitation:
- Integration gate passed or explicitly deferred:
- Reviewer:

## Instructor checkpoint, 22 November 2026

- Starting point was Session 14 on the verified remote commit `f5571ab`.
- The original pool contained 100 draft cases and 28 apparent scope conflicts.
  Normalizing the `Windows 11` platform label resolved 22. Replaying the
  original pool then left six mobile cases. The candidate adjusts those six
  and retains the original IDs, tickets and splits.
- The separate candidate file contains 100 source-checked draft cases, including
  ten unanswerables. It has zero platform-scope conflicts. KB-1034 and KB-1035
  occur in both splits after the platform-neutral mobile email corrections.
- `copilot rag-evaluate` and `scripts/session.py run 15` produced identical
  reports. An exported learner project reproduced the integrated report
  byte for byte. The standalone solution passed 52 tests and the integrated app
  passed 124. The starter passed its 51 inherited checks and failed the new
  exercise at the missing evaluator. Ruff and the authenticated API smoke test passed.

| Metric | Development baseline | Development current | Heldout baseline | Heldout current |
| --- | ---: | ---: | ---: | ---: |
| Recall@5 | 26.67% | 70.00% | 0.00% | 76.67% |
| Context precision | 8.60% | 18.60% | 0.00% | 12.97% |
| Extractive faithfulness | 100.00% | 100.00% | 100.00% | 100.00% |
| Answer relevance | 21.67% | 46.67% | 2.50% | 45.00% |

The report contains the exact-evidence judge configuration, per-metric
denominators, and 1,000-sample paired bootstrap intervals. The Session 5
fixture contains all labelled articles for 20 development cases and zero
heldout answerable cases. The updated index covers all labelled articles.
The heldout recall difference therefore includes a corpus coverage effect.
Faithfulness applies to the cited lines of answers produced by the two
extractive pipelines.

The report records ten observed failures with case IDs and causes. Across the
current pipeline it found 25 retrieval misses, one bad chunk result and 28
downstream answer or abstention failures. It made zero paid calls.

A submission using the draft file was rejected by the
[completion gate](README.md#evidence-and-exit-criteria). After the candidate
and evidence were presented, `amity1415` approved completing the session
and publishing it. The [reviewed copy](../../evals/rag_session15_reviewed.jsonl)
retains the approved evidence, case IDs and split assignments.
