"""Test MMVP metrics engine."""
from __future__ import annotations
import pytest
from core.normalizer import NormalizedResponse, Claim, normalize, _parse_claim
from core.contradiction import detect, _contradicts
from core.confidence import estimate

class TestMetrics:
    def test_agreement_identical(self):
        nr = [NormalizedResponse(model="a", claims=[Claim(text="x", evidence="1")]), NormalizedResponse(model="b", claims=[Claim(text="x", evidence="2")])]
        ctr = detect(nr)
        report = estimate(nr, ctr)
        assert report.agreement == 1.0
        assert report.score == pytest.approx(0.85, rel=1e-3)

    def test_contradiction_detection(self):
        assert _contradicts("true", "false")
        assert _contradicts("increase", "decrease")
        assert not _contradicts("hello", "world")

    def test_contradiction_rate(self):
        nr = [NormalizedResponse(model="a", claims=[Claim(text="true")]), NormalizedResponse(model="b", claims=[Claim(text="false")])]
        ctr = detect(nr)
        assert len(ctr) == 1
        report = estimate(nr, ctr)
        assert report.contradiction_rate == pytest.approx(1.0, rel=1e-3)

    def test_evidence_coverage(self):
        nr = [NormalizedResponse(model="a", claims=[Claim(text="a", evidence="1"), Claim(text="b")])]
        report = estimate(nr, [])
        assert report.evidence_coverage == 0.5

    def test_evidence_provenance(self):
        nr = [NormalizedResponse(model="a", claims=[Claim(text="a", evidence="1"), Claim(text="b")])]
        report = estimate(nr, [])
        assert report.evidence_provenance_score == 0.5

    def test_model_independence(self):
        nr = [NormalizedResponse(model="a", claims=[Claim(text="x")]), NormalizedResponse(model="b", claims=[Claim(text="x")]), NormalizedResponse(model="a", claims=[Claim(text="x")])]
        report = estimate(nr, [])
        assert report.model_independence_score == pytest.approx(2/3, rel=1e-3)

    def test_verification_gain_positive(self):
        nr = [NormalizedResponse(model="a", claims=[Claim(text="a", evidence="1", confidence=0.9)]), NormalizedResponse(model="b", claims=[Claim(text="a", evidence="2", confidence=0.9)])]
        report = estimate(nr, [])
        assert report.verification_gain > 0
