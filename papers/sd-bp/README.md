---
title: "Self-Discovering Build Protocol: Stage-Gated Build Execution v0.1.0"
date: "2026-09-02"
version: "v0.1.0"
language: "en"
status: "frozen"
authors: ["Lord Wilson, BlackSwanLabz"]
keywords: ["SD-BP", "build-discipline", "stage-gates", "minimum-viable-architecture", "adversarial-build"]
repository: "https://github.com/lordwilsonDev/ail-moie-white-papers.git"
paper_id: "sd-bp-v1.0"
---

# Self-Discovering Build Protocol: Stage-Gated Build Execution v0.1.0

## Abstract

Self-Discovering Build Protocol (SD-BP) v1.0 is a build execution discipline layer that sits between IBX Discovery and AIL Inversion. It defines a stage-gated build loop where each stage has a minimum viable artifact, a verification criterion, and a rollback trigger. The protocol prevents over-engineering by requiring explicit "stop" signals between stages. Adversarial build mode is an optional stage that applies inversion to the build itself.

## README

**Purpose:** Execute builds with minimal viable artifacts and explicit stop signals.

**Scope:** Build execution only. Does not define requirements (IBX) or verification (Green-Gate).

**Inputs:** Minimum viable architecture from IBX Discovery.

**Outputs:** Executable artifact + stage gate records.

**Invariant:** Each stage has a minimum viable artifact. No stage may be expanded without explicit authorization.

---

## SPEC

### Stage-Gated Build Loop

| Stage | Minimum Viable Artifact | Verification Criterion | Rollback Trigger |
|-------|------------------------|------------------------|------------------|
| 1. Scaffold | Directory structure + README | Structure exists, README present | Structure invalid |
| 2. Skeleton | Stub files with signatures | All imports resolve | Import error |
| 3. Flesh | First passing test | Test suite green | Test failure |
| 4. Harden | Error handling + logging | Coverage >= 80% | Coverage drop |
| 5. Validate | End-to-end test | E2E passes | E2E failure |

### Stop Signals
- Explicit STOP after each stage
- STOP may be: `continue`, `stop`, `defer`, `invert`
- STOP decisions are recorded in `stage_gate.json`

### Adversarial Build Mode
Optional Stage 6: apply AIL inversion to the build itself.
- Builder: "The build is correct"
- Destroyer: "The build is broken"
- Gate: if Destroyer wins, return to Stage 1

### Rollback Protocol
On rollback trigger:
1. Revert to last green stage
2. Record failure mode in `stage_gate.json`
3. Adjust plan for next attempt
4. Do NOT retry without plan adjustment

---

## RATIONALE

Most builds fail because they skip stages or expand scope without verification. SD-BP enforces a minimum viable artifact at each stage, preventing "blank page" paralysis and "gold plating" simultaneously. The stop signals make the build self-regulating: no external manager required.

---

## RESEARCH

**IBX integration:** IBX produces the minimum viable architecture that SD-BP's Stage 1 scaffolds.

**AIL integration:** SD-BP adversarial mode uses AIL inversion crew to challenge the build.

**BSL integration:** BSL Capability Fabric routes the build to minimum capable specialists per stage.

---

## EXAMPLES

### Example 1: Standard build
```
Stage 1: Scaffold → README present, STOP=continue
Stage 2: Skeleton → imports resolve, STOP=continue
Stage 3: Flesh → first test green, STOP=continue
Stage 4: Harden → coverage 82%, STOP=continue
Stage 5: Validate → E2E passes, STOP=stop (build complete)
```

### Example 2: Adversarial build
```
Stage 1-5: Complete, all green
Stage 6: Adversarial
  Builder: "API correctly validates input"
  Destroyer: "API bypasses validation on OPTIONS preflight"
  Result: DESTROYER WINS
  Action: Rollback to Stage 2, add OPTIONS handling
```

### Example 3: Rollback
```
Stage 3: Flesh → test failure
Rollback Trigger: Test failure
Action: Revert to Stage 2, adjust plan
Next Attempt: Add missing dependency, rerun
```

---

## CHECKLIST

- [ ] Minimum viable architecture received from IBX
- [ ] Stage 1 scaffold created
- [ ] Each stage has minimum viable artifact
- [ ] Verification criterion defined per stage
- [ ] Rollback trigger defined per stage
- [ ] Stop signal issued after each stage
- [ ] `stage_gate.json` written with STOP decision
- [ ] Adversarial build mode executed (optional)
- [ ] On rollback: plan adjustment recorded
- [ ] Final artifact verified against IBX requirements
- [ ] No stage expanded without explicit authorization