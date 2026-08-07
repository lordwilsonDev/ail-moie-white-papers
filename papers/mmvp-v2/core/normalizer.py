"""Response normalizer for MMVP."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Claim:
    text: str
    evidence: str = ""
    confidence: float = 0.0
    source: str = ""

@dataclass
class NormalizedResponse:
    model: str
    claims: List[Claim] = field(default_factory=list)
    raw: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

def normalize(response: Any) -> NormalizedResponse:
    if response is None:
        raise ValueError("response is None")
    text = getattr(response, "text", None) or str(response)
    model = getattr(response, "model", "unknown")
    meta = getattr(response, "metadata", {}) or {}
    claims = [_parse_claim(line) for line in text.splitlines() if line.strip()]
    return NormalizedResponse(model=model, claims=claims, raw=text, metadata=meta)

def _parse_claim(line: str) -> Claim:
    evidence = ""
    confidence = 0.5
    if "evidence:" in line.lower():
        parts = line.split(":", 1)
        evidence = parts[1].strip() if len(parts) > 1 else ""
    return Claim(text=line.strip(), evidence=evidence, confidence=confidence)
