"""
blind.py — blinding and rating-sheet generation.

The integrity of the benchmark rests on raters never seeing which condition
produced an output. This module:

  1. assigns every output an opaque item ID
  2. strips condition-identifying markers from output text
  3. shuffles items and emits rater CSVs (one per rater, independently shuffled)
  4. writes the condition key to a SEPARATE file and prints its SHA-256

Procedure: commit the key hash publicly (e.g. in the pre-registration DOI or a
timestamped post) BEFORE collecting ratings. The hash proves the mapping was
fixed in advance without revealing it. Publish the key itself only after
ratings are locked. This is what makes "blinded" a verifiable claim rather
than an assertion.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import random
import re
import uuid

# text that would leak the condition to a rater
LEAK_PATTERNS = [
    (re.compile(r"\b(inversion critic|positive deviant scout|mechanism synthesizer)\b", re.I), "the analyst"),
    (re.compile(r"\bmixture of inversion experts\b|\bMoIE\b", re.I), "the method"),
    (re.compile(r"\baxiom inversion logic\b|\bAIL\b"), "the method"),
    (re.compile(r"\bunified inversion model\b|\bUIM\b", re.I), "the model"),
    (re.compile(r"\bchain[- ]of[- ]thought\b|\btree[- ]of[- ]thoughts?\b", re.I), "the approach"),
    (re.compile(r"\bstep\s+\d+\s*[—–-]\s*(assumption extraction|inversion|enabling conditions|anomaly discovery|adversarial critique)", re.I), "Analysis"),
    (re.compile(r"^\s*\[DRY RUN PLACEHOLDER[^\]]*\]\s*$", re.M), ""),
    (re.compile(r"\bcondition\s+C[1-5]\b", re.I), "this analysis"),
]

RUBRIC_DIMS = ["novelty", "coherence", "plausibility", "testability", "usefulness"]


def scrub(text: str) -> str:
    for pat, repl in LEAK_PATTERNS:
        text = pat.sub(repl, text)
    return text.strip()


def build(runs_path: str, outdir: str, n_raters: int, seed: int) -> None:
    data = json.loads(pathlib.Path(runs_path).read_text())
    rng = random.Random(seed)
    out = pathlib.Path(outdir)
    (out / "sheets").mkdir(parents=True, exist_ok=True)

    items, key = [], []
    for r in data["runs"]:
        item_id = uuid.UUID(int=rng.getrandbits(128)).hex[:12]
        items.append({"item_id": item_id, "text": scrub(r["output"])})
        key.append({
            "item_id": item_id,
            "condition": r["condition"],
            "question_id": r["question_id"],
            "tokens": r["usage"]["total"],
            "n_samples": r.get("n_samples", 1),
        })

    # sealed key
    key_path = out / "CONDITION_KEY.sealed.json"
    key_blob = json.dumps({"run_id": data["run_id"], "key": key},
                          indent=2, sort_keys=True)
    key_path.write_text(key_blob)
    digest = hashlib.sha256(key_blob.encode()).hexdigest()
    (out / "CONDITION_KEY.sha256").write_text(digest + "\n")

    # item corpus (text only, no condition)
    (out / "items.json").write_text(json.dumps(items, indent=2))

    # per-rater sheets, independently shuffled to decorrelate order effects
    for rater in range(1, n_raters + 1):
        order = items[:]
        rng.shuffle(order)
        path = out / "sheets" / f"rater_{rater:02d}.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["item_id", "output_text"] + RUBRIC_DIMS + ["notes"])
            for it in order:
                w.writerow([it["item_id"], it["text"]] + [""] * len(RUBRIC_DIMS) + [""])

    print(f"items: {len(items)}")
    print(f"rater sheets: {n_raters} -> {out/'sheets'}")
    print(f"\nCONDITION KEY SHA-256:\n  {digest}")
    print("\nCommit this hash publicly BEFORE collecting ratings.")
    print("Do not open CONDITION_KEY.sealed.json until ratings are locked.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs")
    ap.add_argument("--out", default="blinded")
    ap.add_argument("--raters", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260806)
    a = ap.parse_args()
    build(a.runs, a.out, a.raters, a.seed)
