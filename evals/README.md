# evals/

Datasets, rubrics and runners that measure the system. Evaluation data is written by learners, from the historical tickets in `data/tickets/`.

| Path | Created in | Holds |
| --- | --- | --- |
| `rag/golden.jsonl` | Session 5, grown in session 15 | Question, expected article IDs, reference answer; about 100 rows, 10 with no answer in the knowledge base |
| `redteam/attacks.jsonl` | Session 28 | About 25 attacks: instructions hidden in tickets and documents, permission bypass, requests for other people's data |
| `agent/tasks.jsonl` | Session 35 | About 40 tasks: request, user, expected tool calls, expected end state, forbidden actions |
| `rubrics/*.yaml` | Session 36 | Scoring rubrics for the LLM judges |
| `run_rag_eval.py`, `run_agent_eval.py` | Sessions 15 and 37 | One command each; both run in CI from session 38 |

A golden question is built from a resolved ticket: the ticket text gives the question and its `kb_article_id` gives the expected article. Start with the six acceptance requests and the people in `data/personas.md`.
