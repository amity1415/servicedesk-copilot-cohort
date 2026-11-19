"""Session 10 runnable reference experiment; execute from project root."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from copilot.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["rag-postgres-verify"]))
