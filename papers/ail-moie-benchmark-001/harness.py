"""
harness.py — runs the AIL+MoIE benchmark.

Design note on compute matching
-------------------------------
The central methodological objection to MoIE is that it simply spends more
tokens than single-pass prompting, so any advantage is a compute artifact
rather than a protocol effect. The harness answers this directly:

  1. For each question, run C4 and C5 and record total tokens.
  2. Compute the per-question MoIE budget B = mean(tokens(C4), tokens(C5)).
  3. For each baseline condition c in {C1, C2, C3}, run one pass to measure
     its mean single-pass cost s_c, then set n_c = round(B / s_c), floor 1.
  4. Re-run condition c as best-of-n_c, with the selector cost charged to c.

The result is a compute-matched arm (C1-bon, C2-bon, C3-bon) evaluated
alongside the naive arm. The pre-registered primary test is MoIE against the
compute-matched arm, not against naive single-pass prompting.

Usage:
    export ANTHROPIC_API_KEY=...
    python harness.py --questions questions.json --out runs/ --model <model>
    python harness.py --dry-run --out runs/          # plumbing test, no API
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics
import sys
import uuid
from datetime import datetime, timezone

import conditions as C


def load_questions(path: str) -> list[dict]:
    with open(path) as f:
        qs = json.load(f)
    for q in qs:
        assert "id" in q and "text" in q and "domain" in q, f"malformed question: {q}"
    return qs


def run_question(client, q: dict, baselines=("C1", "C2", "C3")) -> list[C.Run]:
    qid, text = q["id"], q["text"]
    out: list[C.Run] = []

    # --- MoIE arms first: they define the compute budget -------------------
    r4 = C.run_c4(client, qid, text)
    r5 = C.run_c5(client, qid, text)
    out += [r4, r5]
    budget = statistics.mean([r4.usage.total, r5.usage.total])

    # --- naive baselines ---------------------------------------------------
    naive = {}
    for c in baselines:
        r = C.CONDITIONS[c](client, qid, text)
        naive[c] = r
        out.append(r)

    # --- compute-matched baselines ----------------------------------------
    for c in baselines:
        s = max(naive[c].usage.total, 1)
        n = max(1, round(budget / s))
        r = C.best_of_n(client, qid, text, C.CONDITIONS[c], n)
        out.append(r)

    return out


# --------------------------------------------------------------------------
# dry run: exercises the whole pipeline with no API calls
# --------------------------------------------------------------------------

def _fake_run(cond: str, qid: str, text: str, rng: random.Random) -> C.Run:
    """Synthetic output for plumbing tests. Contains NO experimental signal."""
    tok = {"C1": 700, "C2": 1100, "C3": 2400, "C4": 6800, "C5": 7600}
    base = tok.get(cond.split("-")[0], 900)
    jitter = rng.randint(-base // 6, base // 6)
    body = (f"[DRY RUN PLACEHOLDER — condition {cond}, question {qid}]\n\n"
            f"{text}\n\n## FALSIFIABLE PREDICTIONS\n"
            "1. placeholder (a) outcome (b) dataset (c) horizon (d) falsifier\n"
            "2. placeholder\n3. placeholder\n")
    return C.Run(cond, qid, text, body, C.Usage(base // 2, (base + jitter) // 2))


def dry_run(questions: list[dict], rng: random.Random) -> list[C.Run]:
    out = []
    for q in questions:
        r4 = _fake_run("C4", q["id"], q["text"], rng)
        r5 = _fake_run("C5", q["id"], q["text"], rng)
        out += [r4, r5]
        budget = statistics.mean([r4.usage.total, r5.usage.total])
        for c in ("C1", "C2", "C3"):
            r = _fake_run(c, q["id"], q["text"], rng)
            out.append(r)
            n = max(1, round(budget / max(r.usage.total, 1)))
            bon = _fake_run(c, q["id"], q["text"], rng)
            bon.condition = c + "-bon"
            bon.n_samples = n
            bon.usage = C.Usage(r.usage.input_tokens * n, r.usage.output_tokens * n)
            out.append(bon)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default="questions.json")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--model", default="claude-sonnet-4-6")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=2000)
    ap.add_argument("--limit", type=int, default=0, help="only first N questions")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", type=int, default=20260806)
    args = ap.parse_args()

    outdir = pathlib.Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    questions = load_questions(args.questions)
    if args.limit:
        questions = questions[: args.limit]

    if args.dry_run:
        runs = dry_run(questions, rng)
        print(f"[dry-run] {len(runs)} synthetic runs over {len(questions)} questions "
              f"— NO experimental signal, plumbing test only", file=sys.stderr)
    else:
        client = C.ModelClient(args.model, temperature=args.temperature,
                               max_tokens=args.max_tokens)
        runs = []
        for i, q in enumerate(questions, 1):
            print(f"[{i}/{len(questions)}] {q['id']} ({q['domain']})", file=sys.stderr)
            runs += run_question(client, q)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model": "DRY-RUN" if args.dry_run else args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "seed": args.seed,
        "dry_run": args.dry_run,
        "n_questions": len(questions),
        "runs": [r.to_dict() for r in runs],
    }
    path = outdir / f"runs-{run_id}.json"
    path.write_text(json.dumps(payload, indent=2))

    # compute-matching audit table
    by_cond: dict[str, list[int]] = {}
    for r in runs:
        by_cond.setdefault(r.condition, []).append(r.usage.total)
    print("\ncondition   n     mean tokens", file=sys.stderr)
    for c in sorted(by_cond):
        v = by_cond[c]
        print(f"{c:<10} {len(v):<5} {statistics.mean(v):>10.0f}", file=sys.stderr)
    print(f"\nwrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
