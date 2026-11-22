# evals/

Datasets, rubrics and runners that measure the system. Evaluation data is written by learners, from the historical tickets in `data/tickets/`.

| Path | Created in | Holds |
| --- | --- | --- |
| `rag_golden.jsonl` | Session 5, grown in session 15 | Frozen draft pool with 100 questions, including 10 unanswerables |
| `rag_session15_candidate.jsonl` | Session 15 | Same 100 case IDs and splits with source excerpts and proposed label corrections |
| `rag_session15_reviewed.jsonl` | Session 15 | Instructor-approved copy used for the completion gate |
| `redteam/attacks.jsonl` | Session 28 | About 25 attacks: instructions hidden in tickets and documents, permission bypass, requests for other people's data |
| `agent/tasks.jsonl` | Session 35 | About 40 tasks: request, user, expected tool calls, expected end state, forbidden actions |
| `rubrics/*.yaml` | Session 36 | Scoring rubrics for the LLM judges |
| `copilot rag-evaluate` | Session 15 | Local paired comparison with four per-split metrics, confidence intervals and attributed failures |

A golden question is built from a resolved ticket: the ticket text gives the question and its `kb_article_id` gives the expected article. Start with the six acceptance requests and the people in `data/personas.md`.
