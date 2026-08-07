"""Runner regression tests."""
from __future__ import annotations
import json
from core.runner import Mission, MissionRunner
from core.dispatcher import Dispatcher, Response


class _StubBackend:
    model = "stub"

    def complete(self, prompt: str, **kwargs):
        return Response(model=self.model, text="stub response", metadata={"mock": True})


def test_runner_returns_report_json():
    question = "What is 2+2?"
    mission = Mission(id="002", objective="smoke", questions=[question], measurements=["agreement"])
    dispatcher = Dispatcher(backends=[_StubBackend()])
    runner = MissionRunner(dispatcher=dispatcher)
    result = runner.run_question(question)
    report = result.report
    raw_json = report.to_json()
    assert json.loads(raw_json)
    assert result.question == question
    assert report.confidence["score"] >= 0
