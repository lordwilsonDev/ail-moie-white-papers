"""
analyze.py — pre-registered analysis for the AIL+MoIE benchmark.

Frozen analysis plan (do not modify after ratings are collected):

  IRR   Krippendorff's alpha (ordinal) per rubric dimension. Items with
        alpha < 0.60 on novelty are flagged and reported, not dropped.

  H1    novelty(C4, C5) > novelty(C1, C2, C3)          [naive arm]
  H1c   novelty(C4, C5) > novelty(C1-bon, C2-bon, C3-bon)
        *** PRIMARY TEST — compute-matched. H1 without H1c is not evidence. ***
  H2    novelty(C5) > novelty(C4)
  H3    coherence(C4, C5) not significantly lower than baselines
        (equivalence test: TOST, margin 0.5 rubric points)

  Tests: Welch's t on rater-mean item scores, plus a paired test across
  questions (each question contributes one score per condition), which is
  the better-powered design. Cohen's d with Hedges' g correction.
  Holm-Bonferroni correction across the family of primary contrasts.

Falsification condition (Section 9): if H1c fails to reach a significant
novelty advantage with g > 0.5 across two independent replications, the
integration claim of the paper is false.
"""

from __future__ import annotations

import argparse
import csv
import glob
import itertools
import json
import pathlib
from collections import defaultdict

import numpy as np
from scipy import stats

DIMS = ["novelty", "coherence", "plausibility", "testability", "usefulness"]
MOIE = ["C4", "C5"]
NAIVE = ["C1", "C2", "C3"]
MATCHED = ["C1-bon", "C2-bon", "C3-bon"]


# --------------------------------------------------------------------------
# Krippendorff's alpha (ordinal difference function)
# --------------------------------------------------------------------------

def krippendorff_alpha(matrix: np.ndarray) -> float:
    """matrix: raters x items, np.nan for missing. Ordinal metric."""
    m = np.asarray(matrix, dtype=float)
    vals = m[~np.isnan(m)]
    if vals.size == 0:
        return float("nan")
    levels = np.unique(vals)
    if levels.size < 2:
        return float("nan")

    # coincidence matrix
    idx = {v: i for i, v in enumerate(levels)}
    k = levels.size
    coin = np.zeros((k, k))
    for col in range(m.shape[1]):
        obs = m[:, col]
        obs = obs[~np.isnan(obs)]
        mu = obs.size
        if mu < 2:
            continue
        for a, b in itertools.permutations(obs, 2):
            coin[idx[a], idx[b]] += 1.0 / (mu - 1)

    n_c = coin.sum(axis=1)
    n_total = coin.sum()
    if n_total == 0:
        return float("nan")

    # ordinal difference metric
    def delta2(c, d):
        lo, hi = (c, d) if c <= d else (d, c)
        s = n_c[lo:hi + 1].sum() - (n_c[c] + n_c[d]) / 2.0
        return s ** 2

    D_o = sum(coin[c, d] * delta2(c, d) for c in range(k) for d in range(k))
    D_e = sum(n_c[c] * n_c[d] * delta2(c, d)
              for c in range(k) for d in range(k) if c != d) / (n_total - 1)

    if D_e == 0:
        return float("nan")
    return 1.0 - (D_o / D_e)


def hedges_g(x: np.ndarray, y: np.ndarray) -> float:
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return float("nan")
    sp = np.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1)) / (nx + ny - 2))
    if sp == 0:
        return float("nan")
    d = (x.mean() - y.mean()) / sp
    J = 1 - 3 / (4 * (nx + ny) - 9)
    return d * J


def holm(pvals: dict[str, float]) -> dict[str, float]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    n = len(items)
    adj, prev = {}, 0.0
    for i, (k, p) in enumerate(items):
        val = min(1.0, max(prev, (n - i) * p))
        adj[k] = val
        prev = val
    return adj


# --------------------------------------------------------------------------
# load
# --------------------------------------------------------------------------

def load(runs_path: str, key_path: str, sheets_glob: str):
    runs = json.loads(pathlib.Path(runs_path).read_text())
    key = {r["item_id"]: r for r in json.loads(pathlib.Path(key_path).read_text())["key"]}

    ratings = defaultdict(lambda: defaultdict(dict))  # dim -> item -> rater -> score
    raters = []
    for path in sorted(glob.glob(sheets_glob)):
        rater = pathlib.Path(path).stem
        raters.append(rater)
        with open(path) as f:
            for row in csv.DictReader(f):
                for d in DIMS:
                    v = (row.get(d) or "").strip()
                    if v:
                        try:
                            ratings[d][row["item_id"]][rater] = float(v)
                        except ValueError:
                            pass
    return runs, key, ratings, raters


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--sheets", default="blinded/sheets/rater_*.csv")
    ap.add_argument("--out", default="results.json")
    a = ap.parse_args()

    runs, key, ratings, raters = load(a.runs, a.key, a.sheets)
    results: dict = {"raters": raters, "irr": {}, "descriptives": {}, "tests": {}}

    if not raters:
        print("No rater sheets found. Nothing to analyze.")
        print("Expected completed CSVs at:", a.sheets)
        return 1

    # ---- IRR -------------------------------------------------------------
    for d in DIMS:
        items = sorted(ratings[d])
        if not items:
            continue
        mat = np.full((len(raters), len(items)), np.nan)
        for j, it in enumerate(items):
            for i, r in enumerate(raters):
                if r in ratings[d][it]:
                    mat[i, j] = ratings[d][it][r]
        results["irr"][d] = krippendorff_alpha(mat)

    alpha_nov = results["irr"].get("novelty", float("nan"))
    print(f"\nInter-rater reliability (Krippendorff alpha, ordinal)")
    for d, v in results["irr"].items():
        flag = "  << below 0.60 threshold" if v == v and v < 0.60 else ""
        print(f"  {d:<13} {v:.3f}{flag}")

    # ---- item means, grouped by condition and question -------------------
    # per_q[dim][condition][question_id] = mean rater score
    per_q = defaultdict(lambda: defaultdict(dict))
    for d in DIMS:
        for item, by_rater in ratings[d].items():
            meta = key.get(item)
            if not meta or not by_rater:
                continue
            per_q[d][meta["condition"]][meta["question_id"]] = float(np.mean(list(by_rater.values())))

    def pool(dim: str, conds: list[str]) -> dict[str, float]:
        """Mean across the listed conditions, per question."""
        qs = set()
        for c in conds:
            qs |= set(per_q[dim].get(c, {}))
        out = {}
        for q in qs:
            vals = [per_q[dim][c][q] for c in conds if q in per_q[dim].get(c, {})]
            if vals:
                out[q] = float(np.mean(vals))
        return out

    print("\nDescriptives (novelty, mean of rater means)")
    for c in NAIVE + MATCHED + MOIE:
        vals = list(per_q["novelty"].get(c, {}).values())
        if vals:
            results["descriptives"][c] = {"mean": float(np.mean(vals)),
                                          "sd": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                                          "n": len(vals)}
            print(f"  {c:<9} n={len(vals):<4} mean={np.mean(vals):.2f}")

    # ---- pre-registered contrasts ----------------------------------------
    contrasts = {
        "H1_moie_vs_naive": ("novelty", MOIE, NAIVE),
        "H1c_moie_vs_computematched": ("novelty", MOIE, MATCHED),
        "H2_c5_vs_c4": ("novelty", ["C5"], ["C4"]),
    }

    raw_p = {}
    for name, (dim, a_conds, b_conds) in contrasts.items():
        A, B = pool(dim, a_conds), pool(dim, b_conds)
        shared = sorted(set(A) & set(B))
        if len(shared) < 3:
            results["tests"][name] = {"status": "insufficient paired data",
                                      "n_paired": len(shared)}
            continue
        x = np.array([A[q] for q in shared])
        y = np.array([B[q] for q in shared])
        t, p = stats.ttest_rel(x, y)
        g = hedges_g(x, y)
        raw_p[name] = float(p)
        results["tests"][name] = {
            "dim": dim, "n_paired": len(shared),
            "mean_a": float(x.mean()), "mean_b": float(y.mean()),
            "t": float(t), "p_raw": float(p), "hedges_g": float(g),
        }

    for name, padj in holm(raw_p).items():
        results["tests"][name]["p_holm"] = padj

    # ---- coherence equivalence (TOST, margin 0.5) ------------------------
    A, B = pool("coherence", MOIE), pool("coherence", MATCHED)
    shared = sorted(set(A) & set(B))
    if len(shared) >= 3:
        diff = np.array([A[q] - B[q] for q in shared])
        se = diff.std(ddof=1) / np.sqrt(len(diff))
        margin = 0.5
        if se > 0:
            p_lo = stats.t.sf((diff.mean() + margin) / se, len(diff) - 1)
            p_hi = stats.t.cdf((diff.mean() - margin) / se, len(diff) - 1)
            results["tests"]["H3_coherence_equivalence"] = {
                "mean_diff": float(diff.mean()), "margin": margin,
                "p_tost": float(max(p_lo, p_hi)),
                "equivalent": bool(max(p_lo, p_hi) < 0.05),
            }

    print("\nPre-registered contrasts")
    for name, r in results["tests"].items():
        if "p_holm" in r:
            verdict = "SUPPORTED" if (r["p_holm"] < 0.05 and r["hedges_g"] > 0.5) else "NOT SUPPORTED"
            star = " ***PRIMARY***" if name.startswith("H1c") else ""
            print(f"  {name}{star}")
            print(f"    n={r['n_paired']}  {r['mean_a']:.2f} vs {r['mean_b']:.2f}  "
                  f"g={r['hedges_g']:.2f}  p_holm={r['p_holm']:.4f}  -> {verdict}")

    prim = results["tests"].get("H1c_moie_vs_computematched", {})
    print("\n" + "=" * 66)
    if "p_holm" in prim:
        if prim["p_holm"] < 0.05 and prim["hedges_g"] > 0.5:
            print("PRIMARY TEST PASSED on this replication.")
            print("Pre-registration requires TWO independent replications.")
        else:
            print("PRIMARY TEST NOT PASSED. Per Section 9, if this holds across")
            print("two independent replications, the integration claim is false")
            print("and must be reported as such.")
    if alpha_nov == alpha_nov and alpha_nov < 0.60:
        print("WARNING: novelty IRR below 0.60 — contrasts are underpowered")
        print("and should be reported with the reliability caveat.")
    print("=" * 66)

    pathlib.Path(a.out).write_text(json.dumps(results, indent=2))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
