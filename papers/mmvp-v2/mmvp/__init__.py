"""MMVP v2.0 verification runner: L0 artifact integrity + L1 functional tests."""
from __future__ import annotations
import os
import subprocess
import sys
from typing import List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED_FILES = [
    "MMVP.md",
    "README.md",
    "SPEC.md",
    "schemas/frontmatter.yaml",
    "examples/metrics_example.json",
    "missions/001_validate_paper.md",
    "missions/002_model_disagreement_test.md",
    "core/canonicalizer.py",
    "core/dispatcher.py",
    "core/normalizer.py",
    "core/contradiction.py",
    "core/confidence.py",
    "core/report.py",
    "core/runner.py",
    "adapters/protocol.py",
    "adapters/http_client.py",
    "adapters/openai_adapter.py",
    "adapters/anthropic_adapter.py",
    "adapters/google_adapter.py",
    "adapters/deepseek_adapter.py",
    "adapters/ollama_adapter.py",
    "adapters/huggingface_adapter.py",
    "cli/mmvp.py",
    "Makefile",
    "pyproject.toml",
    "requirements.txt",
]


def check_artifact_integrity() -> Tuple[int, int]:
    passed = 0
    failed = 0
    for rel in REQUIRED_FILES:
        path = os.path.join(ROOT, rel)
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            passed += 1
        else:
            failed += 1
            print(f"FAIL: {rel} missing or empty")
    return passed, failed


def run_pytest() -> int:
    res = subprocess.run([sys.executable, "-m", "pytest", "tests", "-v"], cwd=ROOT)
    return res.returncode


def main() -> int:
    l0_passed, l0_failed = check_artifact_integrity()
    print(f"L0 Artifact Integrity: {l0_passed} passed, {l0_failed} failed")
    if l0_failed:
        return 1

    print("Running L1 functional tests...")
    rc = run_pytest()
    if rc != 0:
        return rc
    print("L1 Functional Verification: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
