---
title: "BSL AIL Orchestrator: 5-Stage Pipeline with MoIE Routing v0.1.0"
date: "2026-09-02"
version: "v0.1.0"
language: "en"
status: "frozen"
authors: ["Lord Wilson, BlackSwanLabz"]
keywords: ["BSL", "AIL", "orchestrator", "pipeline", "MoIE-routing", "mode-a", "mode-b"]
repository: "https://github.com/lordwilsonDev/ail-moie-white-papers.git"
paper_id: "bsl-ail-orchestrator-v0.1.0"
---

# BSL AIL Orchestrator: 5-Stage Pipeline with MoIE Routing v0.1.0

## Abstract

BSL AIL Orchestrator compresses AIL Operational Execution, IBX Discovery, BSL Capability Fabric, and Green-Gate into a single 5-stage pipeline with rule-based MoIE routing. Mode A handles single-operator tasks (<60s). Mode B handles multi-operator inversions (max 4 operators, 5 LLM call cap). Complexity budgets and falsifiability gates are enforced at the pipeline level, not as afterthoughts.

## README

**Purpose:** One-call invocation for full AIL/BSL/IBX pipeline.

**Scope:** End-to-end orchestration. Does not implement individual stages—delegates to specialist skills.

**Inputs:** Natural-language mission intent.

**Outputs:** Mission outcome + audit record in `ail_runs.db`.

**Invariant:** Pipeline always routes through IBX → Inversion → Execution → Verification. No stage may be skipped.

---

## SPEC

### Pipeline Stages

| Stage | Skill Invoked | Output |
|-------|--------------|--------|
| 1. Identify | ibx-discovery | `mission.json` |
| 2. Invert | inversion-challenge | Inverted claim set |
| 3. Execute | ail-operational-executor | Re-derived claim + delta |
| 4. Verify | green-gate | GREEN/RED verdict |
| 5. Synthesize | bsl-project-steward | Final record |

### MoIE Routing Rules
- Single operator, <60s → Mode A
- Multiple domains or high risk → Mode B
- Mode B: default 4 operators, hard max 6
- 5 LLM call cap per Mode B run

### Complexity Budget
- Hard stop at 6 operators
- Budget checked before Stage 2
- Budget reset after each pipeline run

### Falsifiability Gate
- Gate at Stage 1 (IBX)
- Gate at Stage 3 (Execution)
- Gate at Stage 4 (Verification)
- Failure at any gate → RECYCLE from Stage 1

---

## RATIONALE

Most AIL implementations fail because they treat the pipeline as a suggestion, not a contract. The orchestrator enforces the contract: every mission goes through all five stages. MoIE routing is rule-based to prevent model-based routing from inheriting confirmation bias. The complexity budget prevents runaway escalation.

---

## RESEARCH

**Integration pattern:** The orchestrator is the Hermes skill `bsl-ail-orchestrator`. It loads the four specialist skills in sequence and writes the final record via `bsl-project-steward`. No new code is introduced—the orchestrator is a composition layer.

**AIL alignment:** Matches AIL 5-stage pipeline exactly.

**BSL alignment:** Maps to BSL 7-layer stack (layers 2–5 are the pipeline; layers 1, 6, 7 are framing).

**IBX alignment:** Stage 1 is IBX Discovery. Anti-build gate is enforced before Stage 2.

---

## EXAMPLES

### Example 1: Mode A execution
```
Mission: "Is Python best for ML?"
Mode: A
Duration: 12s
Operators: 1
Delta: 0.58
Verdict: INCONCLUSIVE
```

### Example 2: Mode B execution
```
Mission: "Does rate limiting prevent abuse?"
Mode: B
Operators: 4
Duration: 45s
Delta: 0.82
Verdict: REFUTED
```

### Example 3: Complexity budget enforcement
```
Mission: "Analyze X in 7 domains"
Capability check: 7 operators required
Budget: 6 (hard max)
Decision: DEFER → split into 2 missions
```

---

## CHECKLIST

- [ ] Mission intent received
- [ ] Mode determined (A/B)
- [ ] Operator count within budget
- [ ] Stage 1: IBX Discovery executed
- [ ] Falsifiability gate passed
- [ ] Stage 2: Inversion executed
- [ ] Stage 3: Re-derivation + delta computed
- [ ] Stage 4: Green-Gate verification executed
- [ ] Stage 5: Steward record written
- [ ] Final verdict: SUPPORTED / REFUTED / INCONCLUSIVE / RECYCLE
- [ ] `ail_runs.db` updated with full audit trail
- [ ] Complexity budget reset