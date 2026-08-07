# Mission 001: Run AIL+MoIE Benchmark

**Artifact:** `ail-moie-benchmark-001`  
**Mission ID:** `benchmark-001-run`  
**Status:** PENDING — experiment NOT YET RUN  
**Owner:** lord wilson  
**Date:** 2026-08-06

---

## Objective

Execute the pre-registered AIL+MoIE benchmark to validate the hypothesis that Axiom Inversion Logic + Mixture of Inversion Experts produces higher novelty scores than matched compute baselines.

---

## Pre-Flight Checks

- [ ] Python 3.10+ available (`python3 --version`)
- [ ] Local LLM endpoint configured (Ollama or equivalent)
- [ ] `harness.py` passes smoke test: `python3 harness.py --help`
- [ ] `ail-moie-benchmark.tar.gz` extracted to `./payload/`
- [ ] Output directory `./results/` created
- [ ] SHA256 of `hermes12.bin` matches expected: `sha256sum hermes12.bin`

---

## Execution Steps

### 1. Anonymize outputs
```bash
python3 blind.py \
  --input ./payload/raw_outputs.json \
  --output ./results/blinded.json \
  --seed $RANDOM
```

### 2. Run benchmark conditions
```bash
python3 harness.py \
  --config ./payload/conditions.yaml \
  --output ./results/scored.json \
  --model ollama:llama3.1:8b
```

Conditions expected:
- C1-bon, C2-bon, C3-bon — compute-matched baselines
- C4 — AIL alone
- C5 — AIL+MoIE (treatment)

### 3. Compute effect sizes
```bash
python3 analyze.py \
  --input ./results/scored.json \
  --output ./results/analysis.json \
  --primary H1c
```

Output must include:
- Holm-adjusted p-values for H1c, H2, H3
- Hedges' g with 95% CI
- Decision: REJECT / FAIL TO REJECT / INCONCLUSIVE

---

## Success Criteria

| Hypothesis | Criterion |
|------------|-----------|
| **H1c** (PRIMARY) | Holm-adjusted p < 0.05 AND Hedges' g > 0.5 for novelty(C4,C5) vs baselines |
| **H2** | novelty(C5) > novelty(C4), exploratory |
| **H3** | coherence(C4,C5) not materially lower than baselines (TOST, margin 0.5) |

**Mission PASS:** H1c REJECT with Hedges' g > 0.5  
**Mission FAIL:** H1c FAIL TO REJECT or g ≤ 0.5  
**Mission INCONCLUSIVE:** p < 0.05 uncorrected but Holm-adjusted p ≥ 0.05

---

## Falsification

Per pre-registration:
> If H1c fails across two independent replications, the paper's integration claim is false and must be reported as such.

**This is not a negotiable success criterion.** If falsified, update REGISTRY.json `status` to `falsified` and `experiment_status` to `FAILED`.

---

## Outputs

1. `./results/blinded.json` — anonymized raw outputs
2. `./results/scored.json` — novelty/coherence scores per condition
3. `./results/analysis.json` — statistical analysis with Holm/Hedges
4. `./results/decision.md` — one-paragraph verdict

---

## Rollback

No destructive operations. Re-run from `blind.py` with different seed if randomization confounds results.

---

## Acceptance Test

- [ ] All three output files present
- [ ] `analysis.json` contains `holm_adjusted_p`, `hedges_g`, `decision`
- [ ] `decision.md` matches `analysis.json` conclusion
- [ ] REGISTRY.json `experiment_status` updated to `RUN` or `COMPLETE`
