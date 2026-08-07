"""MMVP v2.0 verification runner."""
from __future__ import annotations
import subprocess
import sys
import os

def verify() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return subprocess.run([sys.executable, "-m", "pytest", "tests", "-v"], cwd=root).returncode

if __name__ == "__main__":
    raise SystemExit(verify())
