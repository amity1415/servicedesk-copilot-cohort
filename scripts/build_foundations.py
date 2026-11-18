# ruff: noqa: E501
"""Create the first four real session implementations without overwriting learner work."""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "scripts/course_sources"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def stub(text, functions):
    class Stub(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name in functions:
                message = f"TODO: implement {node.name} following this session's BUILD_GUIDE.md"
                node.body = [
                    ast.Expr(ast.Constant(message)),
                    ast.Raise(
                        ast.Call(
                            ast.Name("NotImplementedError", ast.Load()), [ast.Constant(message)], []
                        )
                    ),
                ]
            return node

    return ast.unparse(Stub().visit(ast.parse(text))) + "\n"


def cli(stage):
    base = '''"""Cumulative course CLI; this source belongs to the selected session."""
import argparse
import json
import os
from pathlib import Path

from copilot.config import get_settings
from copilot.logging_setup import configure_logging
from copilot.tickets import COUNTABLE_FIELDS, count_by, load_tickets


def main(argv=None):
    parser = argparse.ArgumentParser(prog="copilot")
    commands = parser.add_subparsers(dest="command", required=True)
    stats = commands.add_parser("tickets-stats")
    stats.add_argument("--by", default="category", choices=COUNTABLE_FIELDS)
    stats.add_argument("--path", type=Path)
'''
    if stage >= 2:
        base += """    commands.add_parser("train")
"""
    if stage >= 3:
        base += """    commands.add_parser("compare")
    token_parser = commands.add_parser("token-report")
    token_parser.add_argument("--encoding", default="cl100k_base")
    token_parser.add_argument("--input-price-per-million", type=float)
    token_parser.add_argument("--output-price-per-million", type=float)
"""
    if stage >= 4:
        base += """    commands.add_parser("llm-smoke")
"""
    base += """    args = parser.parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)
    if args.command == "tickets-stats":
        try:
            rows = load_tickets(args.path)
        except FileNotFoundError:
            import logging

            logging.getLogger(__name__).error("ticket export missing; run python -m datagen")
            return 1
        counts = count_by(rows, args.by)
        total = sum(counts.values())
        print(f"{total} tickets by {args.by}")
        for label, count in counts.most_common():
            print(f"  {label}: {count}")
        return 0
"""
    if stage >= 2:
        names = '("train", "compare")' if stage >= 3 else '("train",)'
        arguments = ', neural=args.command == "compare"' if stage >= 3 else ""
        base += f"""    reports = Path(os.getenv("COHORT_REPORT_DIR", "reports"))
    if args.command in {names}:
        from copilot.ml.train import train

        result = train(settings.data_dir, reports{arguments})
        print(json.dumps({{"report": str(reports / "ml.json"), "train": result["train"], "test": result["test"], "models": list(result["models"])}}))
        return 0
"""
    if stage >= 3:
        base += """    if args.command == "token-report":
        from copilot.ml.token_report import measure

        result = measure(settings.data_dir, reports, encoding_name=args.encoding, input_price_per_million=args.input_price_per_million, output_price_per_million=args.output_price_per_million)
        print(json.dumps({"report": str(reports / "tokens.json"), "encoding": result["encoding"], "cost_status": result["cost_status"]}))
        return 0
"""
    if stage >= 4:
        base += """    if args.command == "llm-smoke":
        import httpx

        from copilot.llm.classify import classify
        from copilot.llm.client import ModelClient

        def handle(request):
            text = json.dumps({"category": "Hardware & Devices", "priority": "P3", "summary": "Laptop is slow"})
            return httpx.Response(200, json={"choices": [{"message": {"content": text}}], "usage": {"total_tokens": 20}})
        client = ModelClient("fixture", api_key="fixture", transport=httpx.MockTransport(handle))
        result = classify(client, "My laptop is slow")
        output = {"mode": "offline_schema_fixture", "paid_calls": 0, "classification": result.model_dump(), "accuracy": None, "cost": None, "live_comparison": "requires approved provider, model and budget; not measured"}
        reports.mkdir(parents=True, exist_ok=True)
        (reports / "llm-smoke.json").write_text(json.dumps(output, indent=2))
        print(json.dumps(output))
        return 0
"""
    return (
        base
        + """    parser.error("unknown command")
    return 2
"""
    )


def project_config(stage):
    dependencies = ['"pydantic>=2.7"', '"pydantic-settings>=2.3"']
    if stage >= 2:
        dependencies.append('"scikit-learn>=1.5,<2"')
    if stage >= 3:
        dependencies.append('"tiktoken>=0.7,<1"')
    if stage >= 4:
        dependencies.extend(['"httpx>=0.27,<1"', '"opentelemetry-api>=1.30,<2"'])
    return f"""[project]
name = "servicedesk-copilot-course"
version = "0.{stage}.0"
description = "Completed cumulative IT Copilot source through session {stage:02d}"
requires-python = ">=3.12"
dependencies = [{", ".join(dependencies)}]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.6"]

[project.scripts]
copilot = "copilot.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/copilot"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-q --import-mode=importlib"

[tool.ruff]
line-length = 100
target-version = "py312"
"""


def build():
    sessions = json.loads((ROOT / "sessions/manifest.json").read_text())
    for session in sessions[:4]:
        folder = ROOT / "sessions" / session["folder"]
        if (folder / "starter").exists() or (folder / "solution").exists():
            raise RuntimeError(f"Refusing to overwrite learner/solution work: {folder}")
    # Adopt the same completed implementation in the main project.
    for template, relative in [
        ("ml_train.py", "src/copilot/ml/train.py"),
        ("token_report.py", "src/copilot/ml/token_report.py"),
        ("classify.py", "src/copilot/llm/classify.py"),
    ]:
        write(ROOT / relative, (TEMPLATES / template).read_text(encoding="utf-8"))
    previous = None
    records = []
    tests_by_stage = {
        1: [
            "test_config.py",
            "test_logging_setup.py",
            "test_tickets.py",
            "test_source_identity.py",
        ],
        2: ["test_ml.py"],
        3: ["test_tokens.py"],
        4: ["test_inference.py"],
    }
    all_tests = []
    for stage, session in enumerate(sessions[:4], 1):
        folder = ROOT / "sessions" / session["folder"]
        solution, starter = folder / "solution", folder / "starter"
        earlier_tests = list(all_tests)
        all_tests.extend(tests_by_stage[stage])
        if previous:
            shutil.copytree(previous, solution)
        else:
            for relative in (
                "config.py",
                "logging_setup.py",
                "tickets.py",
                "__init__.py",
                "__main__.py",
            ):
                write(
                    solution / "src/copilot" / relative,
                    (ROOT / "src/copilot" / relative).read_text(encoding="utf-8"),
                )
            for name in (
                "test_config.py",
                "test_logging_setup.py",
                "test_tickets.py",
                "conftest.py",
            ):
                text = (ROOT / "tests" / name).read_text(encoding="utf-8")
                if name == "test_tickets.py":
                    text = text.replace(
                        "from pathlib import Path", "from pathlib import Path\nimport os"
                    )
                    text = text.replace(
                        'EXPORT = Path(__file__).resolve().parents[1] / "data" / "tickets" / "historical_tickets.jsonl"',
                        'EXPORT = Path(os.getenv("COHORT_DATA_DIR", str(Path(__file__).resolve().parents[1] / "data"))) / "tickets/historical_tickets.jsonl"',
                    )
                write(solution / "tests" / name, text)
            write(
                solution / "tests/test_source_identity.py",
                """from pathlib import Path

import copilot


def test_imports_this_checkpoint_not_the_installed_final_app():
    expected = Path(__file__).resolve().parents[1] / "src/copilot"
    assert Path(copilot.__file__).resolve().parent == expected
""",
            )
        write(solution / "pyproject.toml", project_config(stage))
        write(solution / "src/copilot/cli.py", cli(stage))
        write(
            solution / ".gitignore",
            ".venv/\n.work/\nreports/\n__pycache__/\n.pytest_cache/\n.env\n",
        )
        write(solution / ".env.example", "COPILOT_DATA_DIR=data\nCOPILOT_LOG_FORMAT=json\n")
        if stage >= 2:
            text = (TEMPLATES / "ml_train.py").read_text()
            if stage == 2:
                text = text.replace("neural: bool = False", "")
                text = text.replace("reports: Path, )", "reports: Path)")
                text = text.replace("    from sklearn.neural_network import MLPClassifier\n", "")
                text = text.replace(
                    '        if neural:\n            models["mlp"] = MLPClassifier(hidden_layer_sizes=(32,), max_iter=60, random_state=42, early_stopping=True)\n',
                    "",
                )
            write(solution / "src/copilot/ml/__init__.py", '"""Ticket ML experiments."""\n')
            write(solution / "src/copilot/ml/train.py", text)
            write(solution / "tests/test_ml.py", (TEMPLATES / "test_ml.py").read_text())
        if stage >= 3:
            write(
                solution / "src/copilot/ml/token_report.py",
                (TEMPLATES / "token_report.py").read_text(),
            )
            write(solution / "tests/test_tokens.py", (TEMPLATES / "test_tokens.py").read_text())
        if stage >= 4:
            for relative in ("llm/client.py", "telemetry.py"):
                write(
                    solution / "src/copilot" / relative,
                    (ROOT / "src/copilot" / relative).read_text(),
                )
            write(
                solution / "src/copilot/llm/__init__.py",
                '"""Model boundary with explicit offline fixtures."""\n',
            )
            write(solution / "src/copilot/llm/classify.py", (TEMPLATES / "classify.py").read_text())
            write(
                solution / "tests/test_inference.py", (TEMPLATES / "test_inference.py").read_text()
            )
            write(
                solution / ".github/workflows/ci.yml",
                """name: foundations-offline
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python -m pip install -e ".[dev]"
      - run: ruff check .
      - run: ruff format --check .
      - run: pytest
""",
            )
        if previous:
            shutil.copytree(previous, starter)
            # Current acceptance tests describe the new work without shipping its solution.
            for name in tests_by_stage[stage]:
                write(starter / "tests" / name, (solution / "tests" / name).read_text())
            write(starter / "pyproject.toml", project_config(stage))
            if stage == 2:
                text = stub(
                    (solution / "src/copilot/ml/train.py").read_text(),
                    {"read_examples", "request_text", "split_examples", "features", "train"},
                )
                write(starter / "src/copilot/ml/__init__.py", '"""Implement session 2 here."""\n')
                write(starter / "src/copilot/ml/train.py", text)
            if stage == 3:
                write(
                    starter / "src/copilot/ml/token_report.py",
                    stub((TEMPLATES / "token_report.py").read_text(), {"measure"}),
                )
            if stage == 4:
                write(starter / "src/copilot/llm/__init__.py", '"""Implement session 4 here."""\n')
                for name in ("client.py", "classify.py"):
                    text = (solution / "src/copilot/llm" / name).read_text()
                    write(starter / "src/copilot/llm" / name, stub(text, {"complete", "classify"}))
                write(
                    starter / "src/copilot/telemetry.py",
                    (solution / "src/copilot/telemetry.py").read_text(),
                )
        else:
            shutil.copytree(solution, starter)
            for name, functions in [
                ("tickets.py", {"iter_tickets", "count_by"}),
                ("logging_setup.py", {"configure_logging"}),
            ]:
                file = starter / "src/copilot" / name
                write(file, stub(file.read_text(), functions))
        for variant in ("starter", "solution"):
            write(
                folder / variant / "README.md",
                f"""# Session {stage:02d} {variant}

This is actual cumulative Python source, not a launcher into the final app.
Use the project-root runner described in [BUILD_GUIDE.md](../BUILD_GUIDE.md).
The source is under `src/copilot/` and acceptance checks under `tests/`.
Do not install this package into the final application's existing environment.

For a standalone copy, export this checkpoint using the runner. The exporter
adds the shared synthetic data, so the exported project can use its own `.venv`.
""",
            )
        default = {1: ["tickets-stats"], 2: ["train"], 3: ["compare"], 4: ["llm-smoke"]}[stage]
        record = {
            "session": stage,
            "status": "implemented",
            "starter": str(starter.relative_to(ROOT).as_posix()),
            "solution": str(solution.relative_to(ROOT).as_posix()),
            "previous_tests": earlier_tests,
            "new_tests": tests_by_stage[stage],
            "default_command": default,
            "checkpoint_tag": f"cohort-session-{stage:02d}",
            "live_gate": "not run; paid calls disabled" if stage == 4 else None,
        }
        records.append(record)
        guide = f"""# Build session {stage:02d} progressively

## Source and starting point

Open `starter/src/copilot/` to implement this increment. It retains the previous
completed session's source plus explicit new TODOs/tests. `solution/src/copilot/`
is the cumulative reference implementation through this session only. It does not
import the final project's `src/copilot` to implement the lesson.

Read [the problem and data metadata](PROBLEM_STATEMENT_AND_DATASET.md) first.
Run these commands from `D:\\AI-Engineering\\servicedesk-copilot`.

## Before implementation

```powershell
.\\.venv\\Scripts\\python.exe scripts/session.py test {stage} --variant starter
```

The new acceptance tests are expected to fail until the work is implemented.
That expected failure is not a finished session. In sessions 2–4, verify inherited
behaviour separately:

```powershell
{"." + chr(92) + ".venv" + chr(92) + "Scripts" + chr(92) + "python.exe scripts/session.py test " + str(stage) + " --variant starter --previous-only" if stage > 1 else "# Session 1 establishes the initial baseline; there are no previous tests."}
```

## Implement and inspect

{instructions(stage)}

## Run the reference and acceptance checks

```powershell
.\\.venv\\Scripts\\python.exe scripts/session.py run {stage}
.\\.venv\\Scripts\\python.exe scripts/session.py test {stage}
```

To run your own changes, add `--variant starter`. The runner isolates imports to
that tree and checks source identity; it does not replace or stop the API/UI.
Run one training task at a time if sharing CPU/RAM with those services.
Reports go to `reports/cohort/session-{stage:02d}/<variant>/`.

## Compare and integrate

Compare your modified source with `solution/src/copilot/` after attempting the
exercise. Retain the previous contracts, run all accumulated tests and record
actual results in `evidence.md`. The completed ML/tokenization/classification
modules are also adopted in the main project's corresponding packages; the final
API continues to use its existing workflow until its later RAG/agent milestones.

## Export a complete cumulative checkpoint

```powershell
.\\.venv\\Scripts\\python.exe scripts/session.py export {stage} --out .work/checkpoints/session-{stage:02d}
```

The output includes cumulative source, tests, package metadata and the shared seed
data. Choose a fresh destination; existing work is never overwritten. In that
exported folder, create a **separate** virtual environment, install `.[dev]`, then
run `python -m pytest` and `python -m copilot {" ".join(default)}`.
The exported package is the session checkpoint, not the full production release.

After local course tags are created, clone `cohort-session-{stage:02d}` into a new
folder to inspect that exact cumulative Git state. Do not check out a course tag
over the running main application.
"""
        write(folder / "BUILD_GUIDE.md", guide)
        for name in ("README.md", "STEPS_TO_FOLLOW.md"):
            path = folder / name
            text = path.read_text(encoding="utf-8")
            link = (
                "[Actual Python starter solution and cumulative build instructions](BUILD_GUIDE.md)"
            )
            if link not in text:
                first, rest = text.split("\n", 1)
                write(path, first + "\n\n" + link + "\n" + rest)
        write(
            folder / "reference.py",
            f'''"""Run the real session-{stage:02d} solution; source lives in solution/src/copilot."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts/session.py"), "run", "{stage}"], cwd=ROOT))
''',
        )
        previous = solution
    for session in sessions[4:]:
        records.append(
            {
                "session": session["session"],
                "status": "planned",
                "note": "Legacy experiment/preflight remains; real cumulative source is not implemented yet",
            }
        )
    write(
        ROOT / "sessions/implementation_manifest.json",
        json.dumps(
            {
                "scope": "Actual cumulative source readiness, separate from lesson documentation",
                "sessions": records,
            },
            indent=2,
        )
        + "\n",
    )
    shutil.copyfile(TEMPLATES / "session.py", ROOT / "scripts/session.py")
    # Preserve a legacy launcher if the authoring script is deliberately run again.
    author = ROOT / "scripts/build_course.py"
    text = author.read_text(encoding="utf-8")
    text = text.replace(
        '        (directory / "reference.py").write_text(',
        '        if not (directory / "solution").exists():\n            (directory / "reference.py").write_text(',
    )
    # The following arguments are continuation lines inside parentheses, so their
    # indentation does not change the enclosing conditional's scope.
    write(author, text)
    # Make the existing cohort CLI use implemented session source while preserving
    # explicit legacy experiments for the sessions that have not been implemented.
    cli_file = ROOT / "src/copilot/cli.py"
    text = cli_file.read_text(encoding="utf-8")
    needle = "        run_session(args.number, Path.cwd())"
    replacement = """        implementation_manifest = Path.cwd() / "sessions/implementation_manifest.json"
        if implementation_manifest.exists():
            import json
            import subprocess
            import sys

            implementations = json.loads(implementation_manifest.read_text())["sessions"]
            if any(item["session"] == args.number and item["status"] == "implemented" for item in implementations):
                return subprocess.call([sys.executable, str(Path.cwd() / "scripts/session.py"), "run", str(args.number)])
        run_session(args.number, Path.cwd())"""
    if needle not in text:
        raise RuntimeError("Main CLI changed; inspect before integrating session runner")
    write(cli_file, text.replace(needle, replacement))
    print(
        "Created actual cumulative starters, solutions and tests for sessions 01–04; sessions 05–40 remain explicitly planned"
    )


def instructions(stage):
    return {
        1: "1. Inspect `config.py` and the typed ticket schema before implementing loading.\n2. Implement `iter_tickets` with UTF-8 JSONL parsing, blank-line handling and path/line diagnostics.\n3. Implement `count_by` with an allow-list; do not accidentally group by free text.\n4. Implement `configure_logging` so JSON records retain request correlation and repeated configuration does not duplicate handlers.\n5. Run malformed-record and secret-representation tests, then count the real synthetic export.",
        2: "1. Implement `ml/train.py`: load records and construct request text from only the two authorized feature fields.\n2. Split by normalized short-description groups, not random rows.\n3. Fit TF-IDF on training text only and transform heldout text.\n4. Train logistic models for category and priority; write real metrics, labelled confusion matrices and weakest-class evidence.\n5. Cluster training vectors and inspect recurring terms without calling cluster IDs ground truth.\n6. Add the `train` command in `cli.py`, following the solution only after attempting it.",
        3: "1. Extend the previous `train` function with an explicit `neural` option and the small MLP comparator while retaining the same holdout and vocabulary.\n2. Implement `ml/token_report.py` with a named tokenizer, real token IDs and separate source/request distributions.\n3. Keep cost unknown unless both input/output prices are explicitly provided; distinguish forecast from provider billing.\n4. Add `compare` and `token-report` CLI commands.\n5. Run `scripts/session.py run 3 -- token-report` separately. First use of the tokenizer may download its public encoding cache; no paid model is called. Raw export token counts include metadata/HTML markup and are not a cleaned RAG context budget.",
        4: "1. Implement `llm/client.py` transport deadlines, bounded transient retries and token/latency accounting. Never retry a permanent authentication error.\n2. Implement `llm/classify.py` against its Pydantic schema, permitting at most one output repair.\n3. Treat the user request as data and keep source labels out of prompts.\n4. Add the `llm-smoke` command using a declared offline HTTP fixture and the offline CI workflow.\n5. Run schema/repair/retry tests and keep live accuracy and cost unmeasured until the instructor selects an authorized provider, model and budget.",
    }[stage]


if __name__ == "__main__":
    build()
