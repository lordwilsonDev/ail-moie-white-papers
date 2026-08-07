"""Test MMVP end-to-end mission execution."""
from __future__ import annotations
import pytest
from core.canonicalizer import canonicalize
from core.dispatcher import Dispatcher
from core.normalizer import normalize
from core.contradiction import detect
from core.confidence import estimate
from core.report import VerificationReport
from adapters.mock_adapter import MockBackend

MISSION_QUESTION = "Analyze this research paper. Determine: 1. Main claims 2. Evidence quality 3. Contradictions 4. Confidence score"
MISSION_PROMPT = canonicalize(MISSION_QUESTION)

class TestEndToEnd:
    def setup_method(self):
        self.prompts = {
            MISSION_PROMPT: "Main claims: X.\nEvidence quality: medium.\nContradictions: none.\nConfidence: high."
        }
        self.backend_a = MockBackend("deepseek-mock", self.prompts)
        self.backend_b = MockBackend("qwen-mock", {k: v + " [variant]" for k, v in self.prompts.items()})
        self.backend_c = MockBackend("ollama-mock", {k: v + " [local]" for k, v in self.prompts.items()})

    def test_run_mission_produces_report(self):
        dispatcher = Dispatcher([self.backend_a, self.backend_b, self.backend_c])
        responses = dispatcher.dispatch(MISSION_PROMPT)
        normalized = [normalize(r) for r in responses]
        contradictions = detect(normalized)
        confidence = estimate(normalized, contradictions)
        report = VerificationReport.build(
            question=MISSION_QUESTION,
            prompt=MISSION_PROMPT,
            normalized=normalized,
            contradictions=contradictions,
            confidence=confidence,
        )
        assert report.question == MISSION_QUESTION
        assert len(report.models) == 3
        assert 0.0 <= report.confidence["score"] <= 1.0
        assert 0.0 <= report.confidence["evidence_provenance_score"] <= 1.0
        assert 0.0 <= report.confidence["model_independence_score"] <= 1.0
        assert "verification_gain" in report.confidence
        assert report.timestamp

    def test_report_has_json_output(self):
        dispatcher = Dispatcher([self.backend_a, self.backend_b, self.backend_c])
        responses = dispatcher.dispatch(MISSION_PROMPT)
        normalized = [normalize(r) for r in responses]
        contradictions = detect(normalized)
        confidence = estimate(normalized, contradictions)
        report = VerificationReport.build(
            question=MISSION_QUESTION,
            prompt=MISSION_PROMPT,
            normalized=normalized,
            contradictions=contradictions,
            confidence=confidence,
        )
        payload = report.to_json()
        assert "MMVP Report" not in payload or "timestamp" in payload
        assert "confidence" in payload
