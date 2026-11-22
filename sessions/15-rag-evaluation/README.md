# Session 15: RAG evaluation

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 14 is the starting point. This increment becomes part of the same application and is retained in session 16.

## Engineering objective

Recall needs relevance labels; context precision needs labelled retrieved units; faithfulness needs claim support; relevance needs an answer rubric. Do not relabel lexical overlap as faithfulness. Freeze splits before tuning.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

The evaluation set has 60 development cases and 40 heldout cases, including
ten unanswerable cases. Preserve case IDs, source-ticket references and split
membership when reviewing labels. Compare each question with source scope,
expected article IDs, reference excerpts and the reference answer.

## Reference implementation

- [Candidate evaluation labels](../../evals/rag_session15_candidate.jsonl)
- [Evaluation contracts and scoring](../../src/copilot/rag/evaluation.py)

From the project root, run the integrated command and the independent lesson
solution.

```powershell
.\.venv\Scripts\python.exe -m copilot rag-evaluate
.\.venv\Scripts\python.exe scripts/session.py run 15
```

The paired report replays the saved 20-document Session 5 fixture and evaluates
the current 150-document, recursive TF–IDF extractive pipeline. Both receive
the same case scope. The report records corpus coverage and scores each split
independently. Faithfulness measures verbatim support for answer lines.
Relevance measures the cited answer evidence or appropriate abstention. The
judge configuration, sample sizes, paired bootstrap intervals and failure
examples appear in `reports/integrated/rag/rag-evaluate.json`.

## Deliberate failure exercise

Run the preserved draft file with `--dataset evals/rag_golden.jsonl` and inspect
the flagged mobile cases. In the candidate file, compare the two pipelines'
heldout corpus coverage before interpreting their paired deltas. Attribute
differences to retrieval quality only when the compared pipelines share the
relevant source coverage. Retain a regression test for platform filtering.

## Evidence and exit criteria

Review all 100 candidate cases. For each answerable case, accept or correct its
platform, expected sources and verbatim evidence excerpts. For each unanswerable
case, verify the abstention expectation and empty source list. Set each row's
`review_status` to `reviewed` and record the actual `reviewer`. Save the reviewed
copy under `evals/rag_session15_reviewed.jsonl`.

```powershell
.\.venv\Scripts\python.exe scripts/complete_session.py 15 `
  --evaluation-dataset evals/rag_session15_reviewed.jsonl
```

The gate expects four metrics for both pipelines and splits, paired uncertainty,
matching standalone and integrated results, and ten observed failure examples.
Retain the reviewed data and evidence before pushing the completion commit.
