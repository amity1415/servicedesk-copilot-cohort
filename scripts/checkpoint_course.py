"""Create local Git checkpoint tags from validated cumulative source exports.

This never switches the developer working tree, configures a remote or pushes.
The independent course history contains only each completed session's project.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ["-c", "user.name=Codex Course Builder", "-c", "user.email=codex-course@local.invalid"]


def git(*arguments, cwd=ROOT, env=None):
    result = subprocess.run(
        ["git", *IDENTITY, *arguments], cwd=cwd, env=env, text=True, capture_output=True
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def create():
    if (ROOT / ".git").exists():
        raise RuntimeError(
            "A repository already exists; refusing to stage existing work automatically. "
            "Review it and create course refs deliberately."
        )
    manifest_path = ROOT / "sessions/implementation_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    ready = [item for item in manifest["sessions"] if item["status"] == "implemented"]
    if not ready:
        raise RuntimeError("No validated source implementations to checkpoint")
    git("init", "-b", "main")
    paths = [
        ".gitignore",
        ".gitattributes",
        ".dockerignore",
        ".env.example",
        ".pre-commit-config.yaml",
        ".github",
        ".vscode",
        "pyproject.toml",
        "constraints-tested.txt",
        "README.md",
        "RUN_FROM_SCRATCH.md",
        "STEPS_TO_FOLLOW.md",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.app.yml",
        "src",
        "tests",
        "scripts",
        "datagen",
        "data",
        "docs",
        "sessions",
        "policies",
        "evals",
        "telemetry",
        "release",
        "reports/baselines",
    ]
    git("add", "--", *[p for p in paths if (ROOT / p).exists()])
    staged = git("diff", "--cached", "--name-only").splitlines()
    for name in staged:
        path = Path(name)
        if path.name.startswith(".env") and path.name != ".env.example":
            raise RuntimeError("Unapproved environment file staged")
        if any(part in {".venv", ".work", "__pycache__"} for part in path.parts) or path.suffix in {
            ".db",
            ".sqlite3",
            ".pem",
            ".p12",
        }:
            raise RuntimeError(f"Unapproved runtime/credential file staged: {name}")
    git("commit", "-m", "Add reviewed reference application and real foundation session source")
    parent = None
    for item in ready:
        number = item["session"]
        tag = item["checkpoint_tag"]
        destination = ROOT / ".work/checkpoints" / f"{tag}-{uuid.uuid4().hex[:8]}"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/session.py"),
                "export",
                str(number),
                "--out",
                str(destination),
            ],
            cwd=ROOT,
            check=True,
        )
        environment = os.environ.copy()
        environment["GIT_DIR"] = str(ROOT / ".git")
        environment["GIT_WORK_TREE"] = str(destination)
        index = ROOT / ".git" / f"course-index-{uuid.uuid4().hex}"
        environment["GIT_INDEX_FILE"] = str(index)
        try:
            git("read-tree", "--empty", cwd=destination, env=environment)
            git("add", "--all", cwd=destination, env=environment)
            tree = git("write-tree", cwd=destination, env=environment)
        finally:
            index.unlink(missing_ok=True)
        arguments = ["commit-tree", tree]
        if parent:
            arguments.extend(["-p", parent])
        arguments.extend(
            ["-m", f"Completed cumulative course project through session {number:02d}"]
        )
        commit = git(*arguments)
        git(
            "tag",
            "-a",
            tag,
            "-m",
            f"Validated local course checkpoint for session {number:02d}; not a production release",
            commit,
        )
        actual = git("rev-parse", f"{tag}^{{commit}}")
        if actual != commit:
            raise RuntimeError("Checkpoint tag verification failed")
        entries = git("ls-tree", "-r", "--name-only", tag).splitlines()
        if (
            "src/copilot/cli.py" not in entries
            or "data/tickets/historical_tickets.jsonl" not in entries
        ):
            raise RuntimeError("Checkpoint is missing code or seed data")
        if any(name.startswith("sessions/") or name.startswith("services/") for name in entries):
            raise RuntimeError("Checkpoint unexpectedly contains the final application tree")
        item["checkpoint_commit"] = commit
        item["checkpoint_export_verified"] = True
        parent = commit
        print(f"Created {tag}: {commit[:12]}", flush=True)
    manifest["git_history"] = {
        "remote": None,
        "publishing": "not performed",
        "author": "automated Codex Course Builder",
        "root_branch": "main",
        "course_history": "independent linear cumulative source history",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    git("add", "sessions/implementation_manifest.json")
    git("commit", "-m", "Record validated local cumulative course checkpoint identities")
    print("Local Git history is ready; main application working tree was not switched")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create", action="store_true", required=True)
    parser.parse_args()
    create()
