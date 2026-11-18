# ruff: noqa: E501
"""Materialize the session 5–8 RAG batch; validation/commits happen afterwards."""

from __future__ import annotations

import ast
import csv
import json
import os
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "scripts/rag_sources"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def source(name):
    return (PAYLOAD / name).read_text(encoding="utf-8")


def stub(text, names):
    class Rewrite(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name in names:
                message = f"TODO: implement {node.name}; see this session's BUILD_GUIDE.md"
                node.body = [
                    ast.Raise(
                        ast.Call(
                            ast.Name("NotImplementedError", ast.Load()), [ast.Constant(message)], []
                        )
                    )
                ]
            return node

    return ast.unparse(Rewrite().visit(ast.parse(text))) + "\n"


WRAPPERS = """
def load_document(path: Path) -> Document:
    from copilot.rag.loaders import load_document as parse
    return parse(path)

def ingest(data: Path, output: Path) -> dict:
    from copilot.rag.loaders import ingest as run
    return run(data, output)

def chunk(document: Document, strategy="recursive", size=1200, overlap=120,
          encoder=None, threshold=.55):
    from copilot.rag.chunking import make_chunks
    return make_chunks(document, strategy, size, overlap, encoder, threshold)

def allowed(metadata, role, os_name, region):
    from copilot.rag.loaders import is_allowed
    return is_allowed(metadata, role, os_name, region)
"""

MD_LOADER = '''"""Session 5 reads the trainer-normalized Markdown corpus only."""
import hashlib
from pathlib import Path
from datetime import date
import yaml


def load_document(path: Path):
    from copilot.rag.pipeline import Document
    if path.suffix != ".md":
        raise ValueError("Mixed-format parsing is introduced in session 6")
    _, header, text = path.read_text(encoding="utf-8").split("---", 2)
    metadata = yaml.safe_load(header)
    return Document(metadata["id"], text.strip(), metadata, str(path), hashlib.sha256(path.read_bytes()).hexdigest())


def ingest(data, output):
    raise NotImplementedError("Bulk mixed-format ingestion is session 6 work")

'''

FIXED_CHUNKER = '''"""Fixed-window baseline. Later sessions introduce structural boundaries."""
import hashlib
import json


def make_chunks(document, strategy="fixed", size=1200, overlap=120, encoder=None, threshold=.55):
    from copilot.rag.pipeline import Chunk
    if not 0 <= overlap < size:
        raise ValueError("invalid size/overlap")
    if strategy != "fixed":
        raise ValueError("This session implements fixed windows only")
    identity = hashlib.sha256(json.dumps({"digest": document.digest, "metadata": document.metadata, "size": size, "overlap": overlap}, sort_keys=True).encode()).hexdigest()[:16]
    return [Chunk(f"{document.id}:fixed:{identity}:{i}", document.id, document.text[start:start + size], dict(document.metadata), document.source) for i, start in enumerate(range(0, len(document.text), size - overlap))]
'''


def integrate_main():
    package = ROOT / "src/copilot/rag"
    for name in ("loaders.py", "chunking.py", "semantic_encoder.py", "service.py", "cli.py"):
        write(package / name, source(name))
    pipeline = package / "pipeline.py"
    tree = ast.parse(pipeline.read_text())
    replacements = {
        node.name: node for node in ast.parse(WRAPPERS).body if isinstance(node, ast.FunctionDef)
    }
    original_classes = []
    for index, node in enumerate(tree.body):
        if isinstance(node, ast.FunctionDef) and node.name in replacements:
            tree.body[index] = replacements[node.name]
        if isinstance(node, ast.ClassDef) and node.name in {"Document", "Chunk"}:
            original_classes.append(ast.unparse(node))
    write(pipeline, ast.unparse(tree) + "\n")
    contract = (
        "from __future__ import annotations\nfrom dataclasses import dataclass\nfrom pathlib import Path\n\n"
        + "\n\n".join(original_classes)
        + WRAPPERS
    )
    cli = ROOT / "src/copilot/cli.py"
    text = cli.read_text()
    if "register_rag(commands)" not in text:
        text = text.replace(
            "    register(commands)\n",
            "    register(commands)\n\n    from copilot.rag.cli import register as register_rag\n\n    register_rag(commands)\n",
        )
    needle = '    foundation_result = execute(args, settings, Path("reports/integrated"))'
    assert needle in text
    if "rag_result = execute_rag" not in text:
        text = text.replace(
            needle,
            "    from copilot.rag.cli import execute as execute_rag\n\n    rag_result = execute_rag(args, settings)\n    if rag_result is not None:\n        return rag_result\n\n"
            + needle,
        )
    text = text.replace(
        "engine = Engine(runtime, Retriever.from_data(settings.data_dir))",
        "from copilot.rag.service import VectorRag\n\n        engine = Engine(runtime, VectorRag.from_data(settings.data_dir))",
    )
    # Remove the now-unused local Retriever import; root lexical reference remains available.
    text = text.replace("        from copilot.rag.pipeline import Retriever\n", "")
    write(cli, text)
    for relative in ("src/copilot/api/app.py", "src/copilot/mcp_servers/servers.py"):
        path = ROOT / relative
        text = path.read_text()
        text = text.replace(
            "from copilot.rag.pipeline import Retriever, ingest",
            "from copilot.rag.pipeline import ingest\nfrom copilot.rag.service import VectorRag",
        )
        text = text.replace(
            "from copilot.rag.pipeline import Retriever",
            "from copilot.rag.service import VectorRag",
        )
        text = text.replace("Retriever.from_data(data)", "VectorRag.from_data(data)")
        text = text.replace('"mode": "offline-reference"', '"mode": "tfidf-vector-extractive"')
        write(path, text)
    pyproject = ROOT / "pyproject.toml"
    text = pyproject.read_text()
    marker = "[project.optional-dependencies]"
    if "rag-local =" not in text:
        text = text.replace(
            marker,
            marker
            + '\nrag-local = ["onnxruntime>=1.20,<2", "tokenizers>=0.20,<1", "huggingface-hub>=0.26,<2"]',
        )
    write(pyproject, text)
    runner = ROOT / "scripts/session.py"
    text = runner.read_text()
    marker = '    environment["PYTHONPATH"] = str(snapshot / "src")'
    text = text.replace(
        marker,
        marker
        + '\n    environment["COPILOT_LOCAL_MODEL_DIR"] = str(ROOT / ".work/models/minilm")\n    environment.setdefault("OMP_NUM_THREADS", "1")\n    environment.setdefault("OPENBLAS_NUM_THREADS", "1")',
    )
    write(runner, text)
    return contract


def prepare_assets():
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    from copilot.rag.loaders import load_document
    from datagen.content.runbooks import ALL as RUNBOOKS

    metadata = {}
    with (ROOT / "data/policies/register.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            metadata["policies/" + row["file"]] = {
                "audience": "employee",
                "os": "any",
                "region": "global",
                "trust_basis": "Authored policy scope inspected; register controls version/effective status",
            }
    for runbook in RUNBOOKS:
        metadata[f"runbooks/{runbook.id}.docx"] = {
            "id": runbook.id,
            "title": runbook.title,
            "audience": "it-staff",
            "os": "any",
            "region": "global",
            "status": "current",
            "owner": runbook.group,
            "version": runbook.version,
            "effective_date": str(runbook.effective),
            "risk": runbook.risk,
            "approval": runbook.approval,
        }
    for path in (ROOT / "data/reference").glob("*"):
        metadata["reference/" + path.name] = {
            "id": "REF-" + path.stem.upper().replace("_", "-"),
            "title": path.stem.replace("_", " "),
            "audience": "employee",
            "os": "any",
            "region": "global",
            "status": "current",
            "effective_date": "2026-11-13",
            "owner": "Synthetic course source owner",
        }
    reference_records = json.loads(
        '{"reference/glossary.md": {"id": "REF-003", "title": "Glossary of IT terms and abbreviations", "audience": "employee", "os": "any", "region": "global", "status": "current", "effective_date": "2026-09-01", "owner": "Service Desk L1", "version": "1.4"}, "reference/sla_matrix.pdf": {"id": "REF-001", "title": "IT Service Level Targets", "audience": "employee", "os": "any", "region": "global", "status": "current", "effective_date": "2026-01-05", "owner": "Head of IT Service Management", "version": "3.0"}, "reference/software_catalogue.csv": {"id": "REF-002", "title": "Software catalogue", "audience": "employee", "os": "any", "region": "global", "status": "current", "effective_date": "2026-11-02", "owner": "IT Asset Manager", "version": "2026.11"}, "reference/software_catalogue.html": {"id": "REF-002", "title": "Software catalogue", "audience": "employee", "os": "any", "region": "global", "status": "current", "effective_date": "2026-11-02", "owner": "IT Asset Manager", "version": "2026.11"}}'
    )
    metadata.update(reference_records)
    write(ROOT / "policies/source_metadata.json", json.dumps(metadata, indent=2) + "\n")
    cases = [
        {
            "id": "rag05-01",
            "question": "How do I set up VPN on my Mac?",
            "expected_articles": ["KB-1017"],
            "os": "macos",
            "source_ticket": None,
            "review_status": "draft",
            "origin": "acceptance scenario",
        },
        {
            "id": "rag05-02",
            "question": "VPN fails with error 809 on my Windows laptop",
            "expected_articles": ["KB-1018"],
            "os": "windows",
            "source_ticket": None,
            "review_status": "draft",
            "origin": "acceptance scenario",
        },
    ]
    ids = {"KB-1017", "KB-1018"}
    tickets = [
        json.loads(line)
        for line in (ROOT / "data/tickets/historical_tickets.jsonl").read_text().splitlines()
    ]
    for ticket in tickets:
        article = ticket.get("kb_article_id")
        if article and article not in ids:
            ids.add(article)
            cases.append(
                {
                    "id": f"rag05-{len(cases) + 1:02d}",
                    "question": ticket["short_description"] + " " + ticket["description"],
                    "expected_articles": [article],
                    "os": "macos" if "mac" in ticket["device_os"].lower() else "windows",
                    "source_ticket": ticket["ticket_id"],
                    "review_status": "draft",
                    "origin": "synthetic historical ticket",
                }
            )
        if len(ids) == 20:
            break
    fixtures = ROOT / "fixtures/rag-baseline"
    for article in sorted(ids):
        path = next(
            p for p in (ROOT / "data/kb").glob(article + ".*") if p.suffix in {".md", ".html"}
        )
        document = load_document(path)
        meta = dict(document.metadata)
        meta.update(
            original_source=path.relative_to(ROOT).as_posix(), original_sha256=document.digest
        )
        write(
            fixtures / "kb" / (article + ".md"),
            "---\n" + yaml.safe_dump(meta, sort_keys=True) + "---\n\n" + document.text + "\n",
        )
    write(fixtures / "questions.jsonl", "".join(json.dumps(case) + "\n" for case in cases))
    write(
        fixtures / "README.md",
        "# RAG learning baseline\n\nTwenty trainer-normalized Markdown articles, derived from the original synthetic Markdown/HTML exports, and twenty provisional questions. original_source/original_sha256 preserve lineage. Two questions are acceptance scenarios; eighteen come from historical tickets. Labels remain drafts, not human-reviewed ground truth. Original data/evals are unchanged.\n",
    )
    return fixtures


def phase_chunker(stage):
    if stage <= 6:
        return FIXED_CHUNKER
    if stage == 8:
        return source("chunking.py")
    tree = ast.parse(source("chunking.py"))
    tree.body = [
        node
        for node in tree.body
        if not (isinstance(node, ast.FunctionDef) and node.name in {"sections", "semantic_parts"})
    ]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "make_chunks":
            # Retain only fixed and recursive branches; semantic/parents arrive in 8.
            for statement in node.body:
                if (
                    isinstance(statement, ast.If)
                    and ast.unparse(statement.test) == "strategy == 'fixed'"
                ):
                    recursive = statement.orelse[0]
                    recursive.orelse = [
                        ast.Raise(
                            ast.Call(
                                ast.Name("ValueError", ast.Load()),
                                [
                                    ast.Constant(
                                        "This session implements fixed and recursive strategies"
                                    )
                                ],
                                [],
                            )
                        )
                    ]
    return ast.unparse(tree) + "\n"


def build():
    sessions = json.loads((ROOT / "sessions/manifest.json").read_text())
    for item in sessions[4:8]:
        folder = ROOT / "sessions" / item["folder"]
        if (folder / "solution").exists() or (folder / "starter").exists():
            raise RuntimeError("Refusing to overwrite existing RAG learner work")
    contract = integrate_main()
    fixtures = prepare_assets()
    from copilot.rag.semantic_encoder import prepare_model

    os.environ["HF_HUB_DISABLE_XET"] = "1"
    model = prepare_model(ROOT / ".work/models/minilm")
    write(ROOT / "policies/semantic_model.json", json.dumps(model, indent=2) + "\n")
    implementation_path = ROOT / "sessions/implementation_manifest.json"
    implementations = json.loads(implementation_path.read_text())
    previous = ROOT / implementations["sessions"][3]["solution"]
    tests = {
        5: "test_rag_baseline.py",
        6: "test_rag_ingestion.py",
        7: "test_rag_recursive.py",
        8: "test_rag_semantic.py",
    }
    loader_tree = ast.parse(source("loaders.py"))
    visibility = ast.unparse(
        next(
            n for n in loader_tree.body if isinstance(n, ast.FunctionDef) and n.name == "is_allowed"
        )
    )
    for stage, session in enumerate(sessions[4:8], 5):
        folder = ROOT / "sessions" / session["folder"]
        solution, starter = folder / "solution", folder / "starter"
        shutil.copytree(
            previous,
            solution,
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "reports"),
        )
        package = solution / "src/copilot/rag"
        write(package / "__init__.py", '"""Cumulative local RAG implementation."""\n')
        write(package / "pipeline.py", contract)
        write(
            package / "loaders.py",
            MD_LOADER + visibility + "\n" if stage == 5 else source("loaders.py"),
        )
        write(package / "chunking.py", phase_chunker(stage))
        for name in ("service.py", "cli.py"):
            write(package / name, source(name))
        if stage >= 8:
            write(package / "semantic_encoder.py", source("semantic_encoder.py"))
            shutil.copyfile(
                ROOT / "policies/semantic_model.json", solution / "policies/semantic_model.json"
            )
        if not (solution / "fixtures/rag-baseline").exists():
            shutil.copytree(fixtures, solution / "fixtures/rag-baseline")
        (solution / "policies").mkdir(exist_ok=True)
        shutil.copyfile(
            ROOT / "policies/source_metadata.json", solution / "policies/source_metadata.json"
        )
        text = (solution / "src/copilot/cli.py").read_text()
        if "from copilot.rag.cli import register" not in text:
            marker = "    args = parser.parse_args(argv)"
            text = text.replace(
                marker,
                f"    from copilot.rag.cli import register\n\n    register(commands, stage={stage})\n\n"
                + marker,
            )
            marker = "    configure_logging(settings.log_level, settings.log_format)"
            text = text.replace(
                marker,
                marker
                + f"\n\n    from copilot.rag.cli import execute\n\n    rag_result = execute(args, settings, stage={stage})\n    if rag_result is not None:\n        return rag_result",
            )
        else:
            text = text.replace(f"stage={stage - 1}", f"stage={stage}")
        write(solution / "src/copilot/cli.py", text)
        config = (solution / "pyproject.toml").read_text()
        config = config.replace(f'version = "0.{stage - 1}.0"', f'version = "0.{stage}.0"')
        config = config.replace(f"through session {stage - 1:02d}", f"through session {stage:02d}")
        config = config.replace(
            "dependencies = [",
            'dependencies = ["PyYAML>=6,<7", ' if stage == 5 else "dependencies = [",
            1,
        )
        if stage == 6:
            config = config.replace(
                "dependencies = [",
                'dependencies = ["beautifulsoup4>=4.12,<5", "pypdf>=5,<8", "python-docx>=1.1,<2", ',
                1,
            )
        if stage == 8:
            config = config.replace(
                "[project.optional-dependencies]",
                '[project.optional-dependencies]\nrag-local = ["onnxruntime>=1.20,<2", "tokenizers>=0.20,<1", "huggingface-hub>=0.26,<2"]',
            )
        write(solution / "pyproject.toml", config)
        write(solution / "tests" / tests[stage], source(tests[stage]))
        shutil.copytree(
            previous,
            starter,
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "reports"),
        )
        shutil.copyfile(solution / "pyproject.toml", starter / "pyproject.toml")
        write(starter / "tests" / tests[stage], source(tests[stage]))
        if stage == 5:
            for name in ("__init__.py", "pipeline.py", "loaders.py"):
                write(starter / "src/copilot/rag" / name, (package / name).read_text())
            write(starter / "src/copilot/rag/chunking.py", stub(FIXED_CHUNKER, {"make_chunks"}))
            write(
                starter / "src/copilot/rag/service.py",
                stub(source("service.py"), {"__init__", "search", "answer"}),
            )
            shutil.copytree(fixtures, starter / "fixtures/rag-baseline")
        before_tests = [p.name for p in (previous / "tests").glob("test_*.py")]
        item = implementations["sessions"][stage - 1]
        item.update(
            status="implemented",
            completion_state="batch_unverified",
            starter=starter.relative_to(ROOT).as_posix(),
            solution=solution.relative_to(ROOT).as_posix(),
            previous_tests=before_tests,
            new_tests=[tests[stage]],
            default_command={
                5: ["rag-demo"],
                6: ["rag-ingest"],
                7: ["rag-chunks"],
                8: ["rag-benchmark"],
            }[stage],
            checkpoint_tag=f"cohort-session-{stage:02d}",
            live_gate="Live LLM answering and human-label review remain later validation; local retrieval/semantic inference is real",
        )
        write(
            folder / "reference.py",
            f'''"""Execute session {stage} source, not a shared experiment preflight."""
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts/session.py"), "run", "{stage}"], cwd=ROOT))
''',
        )
        write(folder / "BUILD_GUIDE.md", guide(stage))
        for variant in ("starter", "solution"):
            write(
                folder / variant / "README.md",
                f"# Session {stage:02d} {variant}\n\nActual cumulative Python source is in src/copilot. See [BUILD_GUIDE.md](../BUILD_GUIDE.md). Use the root scripts/session.py runner, or export a standalone checkpoint with its own environment. New starter acceptance checks intentionally fail until implemented.\n",
            )
        for name in ("README.md", "STEPS_TO_FOLLOW.md"):
            path = folder / name
            first, rest = path.read_text(encoding="utf-8").split("\n", 1)
            write(
                path, first + "\n\n[Actual cumulative Python build guide](BUILD_GUIDE.md)\n" + rest
            )
        previous = solution
    implementations["validation_batches"] = [
        {
            "sessions": [5, 6, 7, 8],
            "authorization": "Instructor requested implementation through session 8 before batch validation",
            "status": "implementation_ready_validation_pending",
            "session_4_live_check": "separate pending requirement, not silently passed",
        }
    ]
    write(implementation_path, json.dumps(implementations, indent=2) + "\n")
    for test in tests.values():
        shutil.copyfile(PAYLOAD / test, ROOT / "tests" / test)
    write(ROOT / "docs/RAG_SESSION_05_08.md", batch_notes())
    print(
        "Sessions 5–8 implemented as an unverified RAG batch; no completion status or tag is created yet",
        flush=True,
    )


def guide(stage):
    return f"""# Session {stage:02d} actual RAG implementation

This session has cumulative `starter/src/copilot` and `solution/src/copilot` trees.
It inherits the preceding solution and adds { {5: "in-memory vector retrieval and a cited extractive answer", 6: "mixed-format ingestion and trusted metadata", 7: "fixed and recursive chunk inspection", 8: "neural semantic and section parent-child chunking"}[stage] }.

Run from `D:\\AI-Engineering\\servicedesk-copilot`:

```powershell
.\\.venv\\Scripts\\python.exe scripts/session.py test {stage} --variant starter --previous-only
.\\.venv\\Scripts\\python.exe scripts/session.py test {stage} --variant starter
.\\.venv\\Scripts\\python.exe scripts/session.py run {stage}
.\\.venv\\Scripts\\python.exe scripts/session.py test {stage}
```

The untouched starter must retain old behaviour and fail the new acceptance work.
Implement the functions used by `tests/{ {5: "test_rag_baseline.py", 6: "test_rag_ingestion.py", 7: "test_rag_recursive.py", 8: "test_rag_semantic.py"}[stage] }`, then compare with the solution. Read the adjacent problem/data guide; record actual evidence rather than desired metrics.

1. Inspect `rag/pipeline.py` contracts and the current loaders/chunker/service code.
2. Follow the named new acceptance tests from inputs to the missing behaviour.
3. Preserve authorization before scoring and provenance in every result.
4. Run the actual session command and the corresponding root `copilot rag-*` command.
5. Save report paths, run the accumulated tests and participate in the approved 5–8 batch validation.

Session 5 uses twenty trainer-normalized Markdown sources. Some originate from HTML,
including the Mac article; original_source/original_sha256 preserve that lineage.
The twenty questions are drafts, not reviewed golden truth. Session 6 ingests all
150 supported files and reports changes/skips/removals. Session 7 retains atomic
steps even when an atomic unit exceeds the target size. Session 8 uses the pinned
local MiniLM ONNX encoder for semantic boundaries and compares all four strategies
on the same full corpus and questions. Retrieval scoring remains TF-IDF cosine so
the chunking comparison does not also change the retrieval model.

For semantic model preparation (public download, no paid inference):

```powershell
.\\.venv\\Scripts\\copilot.exe rag-model-prepare
```

Use `scripts/session.py run {stage} -- rag-benchmark` for its available strategy
comparison. Session 8's default already runs all four strategies. Reports are under
`reports/cohort/session-{stage:02d}/solution/`; root runs write under
`reports/integrated/rag/`. The answer mode is explicitly extractive. Live LLM
generation, later hybrid/reranking modules and reviewed release quality are not
claimed by this local batch.

Export with `scripts/session.py export {stage} --out .work/checkpoints/session-{stage:02d}`.
Create a separate environment there and install `.[dev]`, plus `[rag-local]` for
session 8's actual neural run. Prepare the pinned model before the semantic command.
Do not install the checkpoint into the running application's environment.
"""


def batch_notes():
    return """# RAG sessions 5 through 8

The instructor authorized implementation of sessions 5–8 as one batch, then actual
validation. Session 4's live-model gate remains pending and is not falsely marked
complete. The exception is explicit; it does not waive this batch's validation.

Implemented scope: twenty-source vector/extractive baseline and draft questions;
full mixed-format ingestion with trusted policy/runbook metadata and invalidation;
fixed/recursive inspection; true local neural semantic boundaries and section-level
parent-child context. TF-IDF cosine is the retrieval baseline, not neural embeddings.
The local sentence encoder is a separate pinned CPU ONNX model used in semantic
chunking. Its weights live under ignored .work/models, never in normal Git history.

The normalized twenty-source fixture is derived from original Markdown/HTML with
source hashes, avoiding an invented Markdown-only origin for the HTML Mac article.
All original data files and existing evaluation labels are retained unchanged.
Additional questions remain draft labels requiring instructor review.

Main CLI: rag-demo, rag-ask, rag-ingest, rag-chunks, rag-benchmark and
rag-model-prepare. The API and documents MCP factory select the same VectorRag
service implementation. Existing role/OS/region/version constraints still apply.
The running service must be restarted to load changed Python modules; a temporary
isolated API smoke test will be used during validation before any restart.

This file describes implementation scope. Validation and completion/commit status
are recorded separately in sessions/implementation_manifest.json and batch evidence.
"""


if __name__ == "__main__":
    build()
