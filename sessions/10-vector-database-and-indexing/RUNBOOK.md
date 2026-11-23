# Session 10 — Persist vectors in pgvector

Store embeddings in PostgreSQL and query the active index. Verify replacement rollback and source withdrawal.

## 1. Open the project and prepare PowerShell

In VS Code, choose **File → Open Folder** and select the repository. Choose
**Terminal → New Terminal** and use PowerShell. Paste one command at a time.
Keep the terminal at the repository root, even when editing session files.

```powershell
Get-Location
Get-Item pyproject.toml
$py = '.\.venv\Scripts\python.exe'
& $py --version
```

If the last command cannot find Python, follow the
[beginner installation walkthrough](../../docs/BEGINNER_RUNBOOK.md#1-set-up-the-learner-checkout).
Set `$py` again whenever you open a new terminal.

**For this session.** Install `rag-local,postgres`, start Docker, and prepare MiniLM.

```powershell
& $py -m pip install -e ".[rag-local,postgres]"
docker compose up -d --wait db
docker compose exec -T db pg_isready -U copilot -d copilot
& $py -m copilot rag-model-prepare
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 10
& $py scripts/session.py test 10
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-10/solution/rag-postgres-verify.json' -Raw | ConvertFrom-Json
$r | Select-Object pgvector_version, dimension, published_chunks, search_document_ids, failed_replace_rolled_back, withdrawn_chunks
$r | Select-Object exact_top5_chunk_ids, approximate_top5_chunk_ids, top5_overlap
```

Check the database version, vector dimension, retrieved sources, rollback result, and withdrawal result.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 10 --variant starter --previous-only
& $py scripts/session.py test 10 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_postgres.py](starter/tests/test_rag_postgres.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/10-vector-database-and-indexing/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | `rag/postgres_index.py` **new** · [reference](solution/src/copilot/rag/postgres_index.py) | Create generation and vector storage with a known model identity and dimension. |
| 2 | `rag/postgres_index.py` **new** · [reference](solution/src/copilot/rag/postgres_index.py) | Implement allowed-source top-k search and atomic replacement or withdrawal. |
| 3 | [rag/service.py](starter/src/copilot/rag/service.py) · [reference](solution/src/copilot/rag/service.py) | Build the configured persistent index and encoder. |
| 4 | `rag/postgres_benchmark.py` **new** · [reference](solution/src/copilot/rag/postgres_benchmark.py) | Use the isolated verifier state to test retrieval, failure rollback, and withdrawal. |

For additional wiring, see [cli.py](solution/src/copilot/cli.py), [rag/cli.py](solution/src/copilot/rag/cli.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 10 --variant starter
& $py scripts/session.py run 10 --variant starter
Get-Item 'reports/cohort/session-10/starter/rag-postgres-verify.json'
git status --short
```

The learner tests and run should both succeed. Confirm a failed replacement preserves the previous index and a successful withdrawal removes the affected chunks. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-postgres-verify
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
