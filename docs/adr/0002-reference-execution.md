# 0002. Separate local reference checks from release measurements

- Status: accepted for teaching reference
- Date: 2026-11-17

The provider, model revision and learner budget have not been selected. Local
checks must work without a paid call and must not manufacture model-quality data.
The API therefore defaults to an explicitly labelled lexical/extractive workflow.
Neural, provider, graph and protocol adapters remain independently inspectable.

Actual grouped-holdout experiments on the synthetic tickets measured:

| Target | Logistic macro F1 | MLP macro F1 | Weakest class |
| --- | --- | --- | --- |
| Category | 0.8453 | 0.8508 | Security |
| Priority | 0.2916 | 0.2250 | P1 |

These results do not justify a more complex classifier for priority. Inspect P1
support and error cases before attributing its poor performance to imbalance or
missing signal. The generated reports preserve support and confusion matrices.

The improved lexical retrieval baseline measured document Recall@5 of 0.7667 on
90 answerable draft questions. Ten additional questions are unanswerable and
excluded from that recall denominator. Labels require review, and context
precision, faithfulness and relevance remain unmeasured. This is below the 0.85
starting retrieval target and is not release evidence.

Actual MCP/A2A SDK tests and the six-scenario cumulative workflow use in-process
HTTP transports. Docker startup, PostgreSQL persistence, neural downloads and
live-model quality require separate runs. This separation costs additional gates
but keeps each claim tied to observed evidence.
