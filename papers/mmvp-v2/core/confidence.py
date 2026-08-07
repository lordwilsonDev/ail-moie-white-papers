"""Confidence estimator for MMVP."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .contradiction import Contradiction
from .normalizer import NormalizedResponse

@dataclass
class ConfidenceReport:
    score: float
    agreement: float
    stability: float
    evidence_coverage: float
    contradiction_rate: float
    evidence_provenance_score: float = 0.0
    model_independence_score: float = 0.0
    verification_gain: float = 0.0
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
    pair_count = _pair_count(normalized)
    ctr = len(contradictions) / max(1, pair_count)
    eps = _evidence_provenance_score(normalized)
    mis = _model_independence_score(normalized)
    vg = _verification_gain(normalized, ctr, ec)
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
        evidence_provenance_score=eps,
        model_independence_score=mis,
        verification_gain=vg,
        details={
            "pair_count": pair_count,
            "normalized_count": len(normalized),
            "unique_models": len({nr.model for nr in normalized}),
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

def _evidence_provenance_score(normalized: List[NormalizedResponse]) -> float:
    if not normalized:
        return 0.0
    total = 0
    supported = 0
    for nr in normalized:
        for c in nr.claims:
            total += 1
            if c.evidence.strip() or c.source.strip():
                supported += 1
    return supported / max(1, total)

def _model_independence_score(normalized: List[NormalizedResponse]) -> float:
    if len(normalized) < 2:
        return 0.0
    models = [nr.model for nr in normalized]
    unique = len(set(models))
    return min(1.0, unique / max(1.0, len(models)))

def _verification_gain(normalized: List[NormalizedResponse], contradiction_rate: float, evidence_coverage: float) -> float:
    if not normalized:
        return 0.0
    single_model_quality = _single_model_quality(normalized[0])
    multi_model_quality = single_model_quality + (0.15 * evidence_coverage) - (0.25 * contradiction_rate)
    multi_model_quality = max(0.0, min(1.0, multi_model_quality))
    return max(0.0, multi_model_quality - single_model_quality)

def _single_model_quality(normalized: NormalizedResponse) -> float:
    claims = normalized.claims
    if not claims:
        return 0.0
    evidence_ratio = sum(1 for c in claims if c.evidence.strip()) / len(claims)
    avg_confidence = sum(c.confidence for c in claims) / len(claims)
    return min(1.0, 0.4 * evidence_ratio + 0.6 * avg_confidence)
