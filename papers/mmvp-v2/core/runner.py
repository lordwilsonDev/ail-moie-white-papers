"""Mission runner for live backend verification."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from .canonicalizer import canonicalize
from .dispatcher import Dispatcher, Backend
from .normalizer import normalize
from .contradiction import detect
from .confidence import estimate
from .report import VerificationReport


@dataclass(frozen=True)
class Mission:
    id: str
    objective: str
    questions: List[str]
    measurements: List[str]


@dataclass
class RunResult:
    mission_id: str
    question: str
    report: VerificationReport
    raw_responses: List[Any]


class MissionRunner:
    def __init__(self, dispatcher: Dispatcher) -> None:
        self.dispatcher = dispatcher

    def run_question(self, question: str, *, prompt: Optional[str] = None) -> RunResult:
        normalized_prompt = prompt or canonicalize(question)
        responses = self.dispatcher.dispatch(normalized_prompt)
        normalized = [normalize(r) for r in responses]
        contradictions = detect(normalized)
        confidence = estimate(normalized, contradictions)
        report = VerificationReport.build(
            question=question,
            prompt=normalized_prompt,
            normalized=normalized,
            contradictions=contradictions,
            confidence=confidence,
        )
        return RunResult(mission_id="", question=question, report=report, raw_responses=responses)

    def run_mission(self, mission: Mission, prompt: Optional[str] = None) -> List[RunResult]:
        results = []
        for question in mission.questions:
            result = self.run_question(question, prompt=prompt)
            results.append(result)
        return results
