# Mission 003 — Live Backend Validation

id: "003"
title: "Live Backend Validation"
objective: |
  Prove MMVP executes against real heterogeneous models, captures provenance,
  normalizes claims, detects contradictions, and emits a confidence report
  without manual intervention.

category: "live_validation"

providers:
  - openai
  - anthropic
  - deepseek
  - ollama

questions:
  - "What is the capital of Australia?"
  - "Explain why the sky appears blue during the day."
  - "Solve: If a train leaves at 60 km/h and another at 80 km/h from the same point in the same direction, how long until they are 40 km apart?"
  - "List one advantage and one disadvantage of microservices."

success_criteria:
  - provider_execution: "3+ independent models respond"
  - provenance: "model, version, and timestamp captured for every response"
  - normalization: "claims extracted from each response"
  - contradiction: "disagreements detected"
  - confidence: "EPS/MIS/VG reported"
  - audit: "reproducible run directory with prompts.json, responses/*.json, report.json, provenance.json"
