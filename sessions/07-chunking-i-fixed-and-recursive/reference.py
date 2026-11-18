"""Session 07 runnable reference experiment; execute from project root."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from copilot.course.experiments import run_session  # noqa: E402

if __name__ == "__main__":
    run_session(7, ROOT)
