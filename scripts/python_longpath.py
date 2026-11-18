"""Windows-only workspace helper for compiled dependencies under long paths.

Usage: python scripts/python_longpath.py -m pytest ...
Prefer a short checkout path for learners, as described in docs/SETUP.md.
"""

import os
import runpy
import sys

if os.name == "nt":
    sys.path[:] = [
        "\\\\?\\" + os.path.abspath(p)
        if p and os.path.isabs(p) and not p.startswith("\\\\?\\")
        else p
        for p in sys.path
    ]
if sys.argv[1:2] == ["-c"]:
    exec(sys.argv[2])
elif sys.argv[1:2] == ["-m"]:
    module = sys.argv[2]
    sys.argv = [module, *sys.argv[3:]]
    runpy.run_module(module, run_name="__main__", alter_sys=True)
else:
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    runpy.run_path(script, run_name="__main__")
