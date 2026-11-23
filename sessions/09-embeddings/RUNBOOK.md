# Session 09 — Embeddings and cache

Generate normalized text vectors, reuse cached embeddings, and compare two CPU encoders on the same questions.

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

**For this session.** Install `rag-local`, then prepare both models.

```powershell
& $py -m pip install -e ".[rag-local]"
& $py -m copilot rag-model-prepare
& $py -m copilot rag-embedding-model-prepare
```

## 2. Run the finished example

The first command runs the completed lesson. The second checks it with
pytest. Wait for the PowerShell prompt before moving to the next command.

```powershell
& $py scripts/session.py run 9
& $py scripts/session.py test 9
```

Inspect the output:

```powershell
$r = Get-Content 'reports/cohort/session-09/solution/rag-embedding-compare.json' -Raw | ConvertFrom-Json
$r | Select-Object mode, hardware, question_count, label_status
$r.models | ConvertTo-Json -Depth 5
```

Inspect model identity and retrieval measurements. Compare an exact-code query as well as a paraphrase.

## 3. Run the learner's tests

```powershell
& $py scripts/session.py test 9 --variant starter --previous-only
& $py scripts/session.py test 9 --variant starter
```

The first command checks the inherited baseline. It should pass before you edit. The final command checks new learner behavior. A new acceptance check should
fail on the untouched starter. Open the first failing test named by PowerShell
under the starter's `tests` folder and look at its input and expected result.
This session's new test files are [test_rag_embeddings.py](starter/tests/test_rag_embeddings.py).

## 4. Write the code

In the VS Code Explorer, open `sessions/09-embeddings/starter/src/copilot`.
The paths below are relative to that folder. Create files marked **new** in the
starter tree. Save with **Ctrl+S** after each change and rerun the final command
from Step 3. Use the reference links to compare one function at a time.

| Order | File | Change to make |
| --- | --- | --- |
| 1 | [rag/semantic_encoder.py](starter/src/copilot/rag/semantic_encoder.py) · [reference](solution/src/copilot/rag/semantic_encoder.py) | Encode batches, normalize vectors, and key the embedding cache by input and model identity. |
| 2 | [rag/service.py](starter/src/copilot/rag/service.py) · [reference](solution/src/copilot/rag/service.py) | Embed chunks and queries with compatible settings and score only the permitted candidates. |
| 3 | `rag/embedding_benchmark.py` **new** · [reference](solution/src/copilot/rag/embedding_benchmark.py) | Compare model quality, timing, and cache behavior against the same questions. |
| 4 | [rag/cli.py](starter/src/copilot/rag/cli.py) · [reference](solution/src/copilot/rag/cli.py) | Expose model preparation and comparison. |

For additional wiring, see [cli.py](solution/src/copilot/cli.py).

Follow the [numbered lab instructions](STEPS_TO_FOLLOW.md) for the deliberate
failure exercise and full exit criteria.

## 5. Run your code and check the result

```powershell
& $py scripts/session.py test 9 --variant starter
& $py scripts/session.py run 9 --variant starter
Get-Item 'reports/cohort/session-09/starter/rag-embedding-compare.json'
git status --short
```

The learner tests and run should both succeed. Compare the first run with a repeat. Record whether unchanged input reused its cached embedding. Save the commands and
observed results in [evidence.md](evidence.md).

To compare with the root application, run:

```powershell
& $py -m copilot rag-embedding-compare
```

The `--variant starter` command above runs your learner code. This comparison
runs the integrated application from the repository root.
