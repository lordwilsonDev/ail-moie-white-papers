"""Contradiction detector for MMVP."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
from .normalizer import NormalizedResponse

@dataclass
class Contradiction:
    claim_a: str
    claim_b: str
    model_a: str
    model_b: str
    severity: str = "medium"

def detect(normalized: List[NormalizedResponse]) -> List[Contradiction]:
    results: List[Contradiction] = []
    seen: set[Tuple[int, int]] = set()
    for i, a in enumerate(normalized):
        for j, b in enumerate(normalized[i+1:], start=i+1):
            key = (id(a), id(b))
            if key in seen:
                continue
            seen.add(key)
            for ca in a.claims:
                for cb in b.claims:
                    if _contradicts(ca.text, cb.text):
                        results.append(Contradiction(ca.text, cb.text, a.model, b.model))
    return results

def _contradicts(a: str, b: str) -> bool:
    if not a or not b:
        return False
    al = a.lower()
    bl = b.lower()
    if al == bl:
        return False
    opposites = [
        ("true", "false"), ("yes", "no"), ("correct", "incorrect"),
        ("increase", "decrease"), ("support", "oppose"), ("agree", "disagree"),
    ]
    for x, y in opposites:
        if (x in al and y in bl) or (y in al and x in bl):
            return True
    return False
