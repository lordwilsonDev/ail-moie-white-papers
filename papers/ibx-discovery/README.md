---
title: "IBX Discovery: Requirements Anti-Build Gate v0.1.0"
date: "2026-09-02"
version: "v0.1.0"
language: "en"
status: "frozen"
authors: ["Lord Wilson, BlackSwanLabz"]
keywords: ["IBX", "requirements-discovery", "anti-build-gate", "knowledge-classification", "assumption-ledger", "adversarial-testing"]
repository: "https://github.com/lordwilsonDev/ail-moie-white-papers.git"
paper_id: "ibx-discovery-v0.1.0"
---

# IBX Discovery: Requirements Anti-Build Gate v0.1.0

## Abstract

IBX Discovery is a knowledge-classification layer that prevents premature building by classifying requirements into four states—Known Knowns, Known Unknowns, Unknown Knowns, Unknown Unknowns—before any implementation begins. It maintains an assumption ledger with risk scores, enforces an anti-build gate that requires falsifiability and baseline evidence, and closes with an adversarial testing loop. IBX is complementary to AIL: AIL inverts claims, IBX classifies knowledge before claims are formed.

## README

**Purpose:** Stop projects that should not start. Prevent building solutions to misclassified problems.

**Scope:** Pre-build discovery only. Does not execute or verify.

**Inputs:** Natural-language intent, existing evidence, constraints.

**Outputs:** Knowledge classification matrix, assumption ledger, anti-build gate decision, baseline definition.

**Invariant:** No BUILD decision without baseline recording and falsifiability assessment.

---

## SPEC

### Four-State Knowledge Classification

| State | Definition | Action |
|-------|-----------|--------|
| Known Knowns | Facts with evidence | Document, do not re-derive |
| Known Unknowns | Gaps identified | Plan acquisition or accept risk |
| Unknown Knowns | Tacit/expert knowledge | Interview/externalize |
| Unknown Unknowns | Not yet discovered | Flag for adversarial loop |

### Assumption Ledger
- Each assumption: `{id, text, risk_score, evidence, status}`
- Risk score: 0.0–1.0
- Status: `pending` → `validated` / `rejected`

### Anti-Build Gate
Gate passes only if:
1. Falsifiability demonstrated for core claim
2. Baseline recorded (what "before" looks like)
3. Minimum viable architecture defined
4. Assumption ledger populated with all critical assumptions

Gate fails → RECYCLE with gap analysis.

### Adversarial Testing Loop
- Crew: Red Team, Blue Team, Steward
- Red Team attacks assumptions
- Blue Team defends with evidence
- Steward records decision
- Loop terminates when Steward certifies OR gate fails

---

## RATIONALE

Most engineering failures are not execution failures—they are knowledge failures. IBX Discovery forces explicit classification of what is known before a single line of code is written. The anti-build gate is a forcing function: if you cannot articulate what "before" looks like, you cannot measure whether the build succeeded. The adversarial loop externalizes the engineer's optimism bias.

---

## RESEARCH

**IBX Master Blueprint v1.0 gaps closed:**
- No runtime schema → `mission.json` + `stage_gate.json`
- No falsifiability check → explicit Stage 1 gate
- No assumption ledger schema → structured ledger with risk scores
- Adversarial crew undefined → Red/Blue/Steward protocol
- No baseline recording → mandatory baseline definition artifact

**Integration with AIL:** AIL's inversion crew operates on claims. IBX produces claims with known falsifiability. Sequence: IBX Discovery → AIL Inversion → AIL Execution.

**Integration with SD-BP:** IBX produces the "minimum viable architecture" that SD-BP's self-discovering build validates stage-by-stage.

---

## EXAMPLES

### Example 1: BUILD decision
```
Intent: "Add feature X to improve retention"
Knowledge Classification:
  Known Knowns: 3
  Known Unknowns: 2
  Unknown Knowns: 1
  Unknown Unknowns: 1
Assumption Ledger: 4 assumptions, 2 validated
Falsifiability: "Retention improves by ≥5% within 30 days"
Baseline: Current retention = 42%
Anti-Build Gate: PASS
Decision: BUILD
```

### Example 2: RECYCLE decision
```
Intent: "Rewrite entire stack in Rust"
Knowledge Classification:
  Known Knowns: 1 (current stack exists)
  Known Unknowns: 8
  Unknown Knowns: 0
  Unknown Unknowns: 5
Assumption Ledger: 9 assumptions, 0 validated
Falsifiability: undefined
Anti-Build Gate: FAIL
Decision: RECYCLE → perform feasibility study
```

### Example 3: Assumption Ledger entry
```
ID: A-001
Text: "Users will adopt feature X within 2 weeks"
Risk Score: 0.7
Evidence: none yet
Status: pending
Action: Run smoke test with 50 users
```

---

## CHECKLIST

- [ ] Intent statement written without solution language
- [ ] Four-state knowledge matrix populated
- [ ] All critical assumptions identified and risk-scored
- [ ] Falsifiability demonstrated for core claim
- [ ] Baseline recorded with measurable metric
- [ ] Minimum viable architecture defined
- [ ] Anti-build gate decision documented
- [ ] Adversarial loop executed (Red/Blue/Steward)
- [ ] Gate decision: BUILD / RECYCLE / DEFER
- [ ] `mission.json` written for downstream AIL execution
- [ ] `stage_gate.json` written for SD-BP validation
- [ ] No solution language in intent statement
- [ ] Steward certification recorded