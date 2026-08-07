"""Confidence estimator for MMVP."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .normalizer import NormalizedResponse
from .contradiction import Contradiction

@dataclass
class ConfidenceReport:
    score: float
    agreement: float
    stability: float
    evidence_coverage: float
    contradiction_rate: float
    details: Dict[str, Any] = field(default_factory=dict)

def estimate(
    normalized: List[NormalizedResponse],
    contradictions: List[Contradiction],
    *,
    agreement_weight: float = 0.4,
    stability_weight: float = 0.2,
    evidence_weight: float = 0.25,
    contradiction_weight: float = 0.15,
) -> ConfidenceReport:
    if not normalized:
        raise ValueError("no normalized responses")
    agreement = _agreement(normalized)
    stability = _stability(normalized)
    ec = _evidence_coverage(normalized)
    ctr = len(contradictions) / max(1, _pair_count(normalized))
    raw = (
        agreement_weight * agreement
        + stability_weight * stability
        + evidence_weight * ec
        - contradiction_weight * ctr
    )
    score = max(0.0, min(1.0, raw))
    return ConfidenceReport(
        score=score,
        agreement=agreement,
        stability=stability,
        evidence_coverage=ec,
        contradiction_rate=ctr,
        details={
            "pair_count": _pair_count(normalized),
            "normalized_count": len(normalized),
        },
    )

def _agreement(normalized: List[NormalizedResponse]) -> float:
    if len(normalized) < 2:
        return 1.0
    texts = [set(c.text.lower() for c in nr.claims) for nr in normalized]
    base = texts[0]
    overlaps = [len(base & t) / max(1, len(base | t)) for t in texts[1:]]
    return sum(overlaps) / max(1, len(overlaps))

def _stability(normalized: List[NormalizedResponse]) -> float:
    if len(normalized) < 2:
        return 1.0
    lens = [len(nr.claims) for nr in normalized]
    if not lens:
        return 1.0
    avg = sum(lens) / len(lens)
    if avg == 0:
        return 1.0
    variance = sum((x - avg) ** 2 for x in lens) / len(lens)
    return max(0.0, 1.0 - min(1.0, variance / max(1.0, avg)))

def _evidence_coverage(normalized: List[NormalizedResponse]) -> float:
    total = 0
    covered = 0
    for nr in normalized:
        for c in nr.claims:
            total += 1
            if c.evidence.strip():
                covered += 1
    return covered / max(1, total)

def _pair_count(normalized: List[NormalizedResponse]) -> int:
    n = len(normalized)
    return n * (n - 1) // 2
