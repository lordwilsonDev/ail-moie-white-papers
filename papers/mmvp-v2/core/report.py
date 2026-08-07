"""Report generator for MMVP."""
from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from .normalizer import NormalizedResponse
from .contradiction import Contradiction
from .confidence import ConfidenceReport

@dataclass
class VerificationReport:
    question: str
    prompt: str
    timestamp: str
    responses: List[Dict[str, Any]] = field(default_factory=list)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    confidence: Dict[str, Any] = field(default_factory=dict)
    models: List[str] = field(default_factory=list)

    @classmethod
    def build(
        cls,
        *,
        question: str,
        prompt: str,
        normalized: List[NormalizedResponse],
        contradictions: List[Contradiction],
        confidence: ConfidenceReport,
    ) -> "VerificationReport":
        return cls(
            question=question,
            prompt=prompt,
            timestamp=datetime.now(timezone.utc).isoformat(),
            responses=[{
                "model": nr.model,
                "claims": [c.text for c in nr.claims],
                "raw": nr.raw,
            } for nr in normalized],
            contradictions=[{
                "claim_a": c.claim_a,
                "claim_b": c.claim_b,
                "model_a": c.model_a,
                "model_b": c.model_b,
                "severity": c.severity,
            } for c in contradictions],
            confidence={
                "score": confidence.score,
                "agreement": confidence.agreement,
                "stability": confidence.stability,
                "evidence_coverage": confidence.evidence_coverage,
                "contradiction_rate": confidence.contradiction_rate,
            },
            models=list({nr.model for nr in normalized}),
        )

    def to_json(self) -> str:
        import json
        return json.dumps({
            "question": self.question,
            "timestamp": self.timestamp,
            "models": self.models,
            "responses": self.responses,
            "contradictions": self.contradictions,
            "confidence": self.confidence,
        }, indent=2)

    def summary(self) -> str:
        lines = [
            f"MMVP Report | {self.timestamp}",
            f"Question: {self.question}",
            f"Models: {', '.join(self.models) if self.models else 'none'}",
            f"Confidence: {self.confidence.get('score', 0.0):.2f}",
            f"Contradictions: {len(self.contradictions)}",
        ]
        return "\n".join(lines)
