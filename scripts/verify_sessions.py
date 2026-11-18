"""Execute all local session references; preserve integration caveats in reports."""

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))

from copilot.course.experiments import run_session  # noqa: E402

results = []
for number in range(1, 41):
    try:
        run_session(number, root)
        results.append({"session": number, "reference_experiment": "passed"})
    except Exception as exc:
        results.append({"session": number, "reference_experiment": "failed", "error": str(exc)})
        print(f"Session {number}: {exc}", flush=True)
summary = {"scope": "local reference experiments, not syllabus release gates", "sessions": results}
(root / "reports/session_validation.json").write_text(json.dumps(summary, indent=2))
if any(r["reference_experiment"] == "failed" for r in results):
    raise SystemExit(1)
print("All 40 local reference experiments ran successfully", flush=True)
