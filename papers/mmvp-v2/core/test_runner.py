"""MMVP runtime test runner."""
from __future__ import annotations

def main() -> int:
    import subprocess, sys
    return subprocess.call([sys.executable, "-m", "pytest", "tests", "-v"])

if __name__ == "__main__":
    raise SystemExit(main())
