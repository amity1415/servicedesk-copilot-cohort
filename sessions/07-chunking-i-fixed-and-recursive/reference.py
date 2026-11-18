"""Execute session 7 source, not a shared experiment preflight."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    raise SystemExit(
        subprocess.call([sys.executable, str(ROOT / "scripts/session.py"), "run", "7"], cwd=ROOT)
    )
