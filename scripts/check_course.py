"""Validate session deliverables and internal Markdown targets without network."""

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sessions = json.loads((root / "sessions/manifest.json").read_text())
assert [s["session"] for s in sessions] == list(range(1, 41))
required = [
    "README.md",
    "STEPS_TO_FOLLOW.md",
    "INSTRUCTOR_NOTES.md",
    "reference.py",
    "evidence.md",
    "PROBLEM_STATEMENT_AND_DATASET.md",
]
errors = []
for session in sessions:
    folder = root / "sessions" / session["folder"]
    for name in required:
        if not (folder / name).is_file():
            errors.append(str(folder / name))
    for document in folder.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if (
                not target.startswith(("http:", "https:", "#"))
                and not (document.parent / target.split("#")[0]).exists()
            ):
                errors.append(f"{document.name}: missing {target}")
if errors:
    raise SystemExit("\n".join(errors))
print("40 session folders validated; all required files and session links exist")
