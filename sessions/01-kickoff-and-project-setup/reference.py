"""Run the real session-01 solution; source lives in solution/src/copilot."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    raise SystemExit(
        subprocess.call([sys.executable, str(ROOT / "scripts/session.py"), "run", "1"], cwd=ROOT)
    )
