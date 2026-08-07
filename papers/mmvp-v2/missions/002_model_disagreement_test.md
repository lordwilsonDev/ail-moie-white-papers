# Mission 002 — Model Disagreement Test

## Objective
Measure how independent LLMs behave on the same question and whether MMVP metrics surface disagreement, evidence quality, and useful novelty.

## Question Mix
### Category A — Facts
Explain the latest state of quantum error correction.

### Category B — Reasoning
Find flaws in this software architecture.

### Category C — Novel Ideas
Design a better agent architecture.

## Measurements
- Agreement rate
- Contradiction rate
- Evidence coverage
- Evidence provenance score
- Model independence score
- Verification gain

## Acceptance Criteria
- At least 3 backends configured
- Mission produces report JSON
- JSON contains all new metric fields
- No absolute correctness claims made
